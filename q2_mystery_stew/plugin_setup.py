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

from qiime2.plugin import Int, Range, UsageAction, UsageInputs, \
                          UsageOutputNames

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

Sig = namedtuple('Sig', ['num_inputs', 'num_outputs', 'signature'])
Param = namedtuple('Param', ['base_name', 'type', 'domain'])

function_signatures = (function_template_1output,
                       function_template_2output,
                       function_template_3output)


class UsageInstantiator:
    def __init__(self, inputs_params, outputs, name):
        self.inputs_params = {}
        for param in inputs_params:
            self.inputs_params.update(param)

        self.outputs = {}
        for output in outputs:
            self.outputs.update({output[0]: str(output[1])})

        self.name = name

    def __call__(self, use):
        use.action(
            UsageAction(plugin_id='mystery_stew', action_id=self.name),
            UsageInputs(**self.inputs_params),
            UsageOutputNames(**self.outputs),
        )


def generate_signatures(args):
    for num_inputs in range(1, len(args) + 1):
        for num_outputs in range(1, len(function_signatures) + 1):
            yield Sig(num_inputs, num_outputs,
                      function_signatures[num_outputs - 1])


int_args = {
    'single_int': Param('single_int', Int, (-4, 0, 4)),
    'int_range_one_arg': Param('int_range_one_arg',
                               Int % Range(5), (-5, 1, 5)),
    'int_range_two_args': Param('int_range_two_args',
                                Int % Range(-5, 5), (-6, 2, 6))
}

num_functions = 0
signatures = generate_signatures(int_args)

for signature in signatures:
    for params in product(int_args.values(),
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
            outputs.append((f'outputs_{i}', EchoOutput))

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

plugin.register_formats(EchoOutputFmt, EchoOutputDirFmt)
plugin.register_semantic_types(EchoOutput)
plugin.register_semantic_type_to_format(EchoOutput, EchoOutputDirFmt)
