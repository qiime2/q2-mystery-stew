# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin import Plugin
from itertools import product
from collections import namedtuple

from qiime2.plugin import Int, Range, Float, Bool, Str, Choices, UsageAction, \
                          UsageInputs, UsageOutputNames

import q2_mystery_stew
from q2_mystery_stew.template import rewrite_function_signature, \
                                     function_template_1output, \
                                     function_template_2output, \
                                     function_template_3output
from q2_mystery_stew.templatable_echo_fmt import EchoOutput, EchoOutputFmt, \
                                                 EchoOutputDirFmt

plugin = Plugin(
    name='mystery-stew',
    version=q2_mystery_stew.__version__,
    website='https://github.com/qiime2/q2-mystery-stew',
    package='q2_mystery_stew',
    description=('This QIIME 2 plugin Templates out arbitrary QIIME 2 actions '
                 'to test interfaces. '),
    short_description='Plugin for generating arbitrary QIIME 2 actions.'
)

Sig = namedtuple('Sig', ['arg_set', 'num_inputs', 'num_outputs', 'signature'])
Param = namedtuple('Param', ['base_name', 'type', 'domain'])

function_signatures = (function_template_1output,
                       function_template_2output,
                       function_template_3output)


class UsageInstantiator:
    def __init__(self, inputs_params, outputs, name):
        self.inputs_params = {}
        for param in inputs_params:
            self.inputs_params.update(param)

        self.outputs = outputs
        self.name = name
        self.output_names = {k: k for k, _ in self.outputs}

    def __call__(self, use):
        use.action(
            UsageAction(plugin_id='mystery_stew', action_id=self.name),
            UsageInputs(**self.inputs_params),
            UsageOutputNames(**self.output_names),
        )

        for name, value in self.inputs_params.items():
            inputs_params = ''.join(f'{name}: {value}\n')

        output1 = use.get_result('output_1')
        output1.assert_has_line_matching(
            label='validate inputs and params',
            path='echo.txt',
            expression=inputs_params,
        )

        if len(self.output_names) > 1:
            output2 = use.get_result('output_2')
            output2.assert_has_line_matching(
                label='validate second',
                path='echo.txt',
                expression='second',
            )

        if len(self.output_names) > 2:
            output3 = use.get_result('output_3')
            output3.assert_has_line_matching(
                label='validate third',
                path='echo.txt',
                expression='third',
            )


def generate_signatures(args):
    for name, arg_set in args.items():
        for num_inputs in range(1, len(arg_set) + 1):
            for num_outputs in range(1, len(function_signatures) + 1):
                yield Sig(name, num_inputs, num_outputs,
                          function_signatures[num_outputs - 1])


int_args = {
    'single_int': Param('single_int',
                        Int, (-1, 0, 1)),
    'int_range_one_arg': Param('int_range_one_arg',
                               Int % Range(3), (-2, 0, 2)),
    'int_range_two_args': Param('int_range_two_args',
                                Int % Range(-3, 4), (-3, 0, 3)),
}

float_args = {
    'single_float': Param('single_float',
                          Float, (-1.5, 0.0, 1.5)),
    'float_range_one_arg': Param('float_range_one_arg',
                                 Float % Range(2.5), (-2.5, 0.0, 2.49)),
    'float_range_two_args': Param('float_range_two_args',
                                  Float % Range(-3.5, 3.5), (-3.5, 0, 3.49)),
}

non_numerical_args = {
    'string': Param('string',
                    Str, ('', 'some string')),
    'string_choices': Param('string_choices',
                            Str % Choices('A', 'B'), ('A', 'B')),
    'boolean': Param('boolean',
                     Bool, (True, False)),
}

args = {
    'ints': int_args,
    'floats': float_args,
    'non_numericals': non_numerical_args,
}

num_functions = 0
signatures = generate_signatures(args)

num_examples = 0
for signature in signatures:
    for params in product(args[signature.arg_set].values(),
                          repeat=signature.num_inputs):
        action_name = f'func_{num_functions}'

        param_dict = {}
        for i, param in enumerate(params):
            param_dict.update({param.base_name + f'_{i}': param})

        # This dictionary allows for easy registration of Qiime parameters
        param_name_to_type_dict = \
            {name: value.type for name, value in param_dict.items()}

        rewrite_function_signature(signature.signature,
                                   {},
                                   param_name_to_type_dict,
                                   signature.num_outputs,
                                   action_name)

        outputs = []
        for i in range(signature.num_outputs):
            outputs.append((f'output_{i + 1}', EchoOutput))

        valid_param_values = [[] for param in range(len(param_dict))]
        for index, name in enumerate(param_dict):
            for valid_param_value in param_dict[name].domain:
                valid_param_values[index].append({name: valid_param_value})

        usage_examples = {}
        for example_number, valid_params in \
                enumerate(product(*valid_param_values)):
            example_name = action_name + f'_{example_number}'
            usage_examples[example_name] = \
                UsageInstantiator(valid_params, outputs, action_name)
            num_examples += 1

        plugin.methods.register_function(
            function=signature.signature,
            inputs={},
            parameters=param_name_to_type_dict,
            outputs=outputs,
            name=action_name,
            description='',
            examples=usage_examples
        )
        num_functions += 1

raise ValueError(num_examples)
plugin.register_formats(EchoOutputFmt, EchoOutputDirFmt)
plugin.register_semantic_types(EchoOutput)
plugin.register_semantic_type_to_format(EchoOutput, EchoOutputDirFmt)
