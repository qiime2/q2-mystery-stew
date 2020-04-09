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
import pandas as pd

import qiime2
from qiime2.plugin import Int, Range, Float, Bool, Str, Choices, List, Set, \
                          Metadata, MetadataColumn, Categorical, Numeric, \
                          UsageAction, UsageInputs, UsageOutputNames
from qiime2.core.type.collection import Tuple

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

Sig = namedtuple('Sig', ['num_inputs', 'num_outputs', 'template'])
Param = namedtuple('Param', ['base_name', 'type', 'domain'])

function_templates = (function_template_1output,
                      function_template_2output,
                      function_template_3output)


class UsageInstantiator:
    def __init__(self, inputs_params, outputs, name):
        self.inputs_params = inputs_params
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
            if 'md' in name:
                value = value.to_dataframe()
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


def generate_signatures():
    for num_inputs in range(1, 4):
        for num_outputs in range(1, len(function_templates) + 1):
            yield Sig(num_inputs, num_outputs,
                      function_templates[num_outputs - 1])


all_params = {
    # int parameters
    'single_int': Param('single_int',
                        Int, (-1, 0, 1)),
    'int_range_1_param': Param('int_range_1_param',
                               Int % Range(3), (-2, 0, 2)),
    'int_range_1_param_i_e': Param('int_range_1_param_i_e',
                                   Int % Range(3, inclusive_end=True),
                                   (-3, 0, 3)),
    'int_range_2_params': Param('int_range_2_params',
                                Int % Range(-3, 4), (-3, 0, 3)),
    'int_range_2_params_i_e': Param('int_range_2_params_i_e',
                                    Int % Range(-3, 4, inclusive_end=True),
                                               (-3, 0, 4)),
    'int_range_2_params_no_i': Param('int_range_2_params_no_i',
                                     Int % Range(-3, 4,
                                                 inclusive_start=False),
                                     (-2, 0, 3)),
    'int_range_2_params_i_e_ex_s': Param('int_range_2_params_i_e_ex_s',
                                         Int % Range(-3, 4,
                                                     inclusive_start=False,
                                                     inclusive_end=True),
                                         (-2, 0, 4)),
    # float parameters
    'single_float': Param('single_float',
                          Float, (-1.5, 0.0, 1.5)),
    'float_range_1_param': Param('float_range_1_param',
                                 Float % Range(2.5), (-2.5, 0.0, 2.49)),
    'float_range_1_param_i_e': Param('float_range_1_param_i_e',
                                     Float % Range(2.5, inclusive_end=True),
                                     (-2.5, 0.0, 2.5)),
    'float_range_2_params': Param('float_range_2_params',
                                  Float % Range(-3.5, 3.5), (-3.5, 0, 3.49)),
    'float_range_2_params_i_e': Param('float_range_2_params_i_e',
                                      Float % Range(-3.5, 3.5,
                                                    inclusive_end=True),
                                      (-3.5, 0, 3.5)),
    'float_range_2_params_no_i': Param('float_range_2_params_no_i',
                                       Float % Range(-3.5, 3.5,
                                                     inclusive_start=False),
                                       (-3.49, 0, 3.49)),
    'float_range_2_params_i_e_ex_s': Param('float_range_2_params_i_e_ex_s',
                                           Float % Range(-3.5, 3.5,
                                                         inclusive_start=False,
                                                         inclusive_end=True),
                                           (-3.49, 0, 3.49)),
    # non-numerical parameters
    'string': Param('string',
                    Str, ('', 'some string')),
    'string_choices': Param('string_choices',
                            Str % Choices('A', 'B'), ('A', 'B')),
    'boolean': Param('boolean',
                     Bool, (True, False)),
    # metedata parameters
    # 'md': Param('md', Metadata, (qiime2.Metadata(pd.DataFrame({'a': '1'},
    #                              index=pd.Index(['0'], name='id'))),)),
    # 'mdc_cat': Param('mdc_cat', MetadataColumn[Categorical],
    #                  (qiime2.CategoricalMetadataColumn(mdc_cat_val),)),
    # 'mdc_num': Param('mdc_num', MetadataColumn[Numeric],
    #                  (qiime2.NumericMetadataColumn(mdc_num_val),)),
    # collection parameters
    # 'int_list': Param('int_list', List[Int], (int_params.values())),
    # 'float_list': Param('float_list', List[Float], (float_params.values())),
    # 'int_set': Param('int_set', Set[Int], (int_params.values())),
    # 'float_set': Param('float_set', Set[Float], (float_params.values())),
    # 'tuple': Param('tuple', Tuple, (int_params, float_params)),
    # 'int_tuple': Param('int_tuple', Tuple[Int], (int_params)),
    # 'float_tuple': Param('float_tuple', Tuple[Float], (float_params))
}

num_functions = 0
signatures = generate_signatures()
for sig in signatures:
    for param_set in product(all_params.values(), repeat=sig.num_inputs):
        for params in zip(param_set):
            action_name = f'func_{num_functions}'

            param_dict = {}
            for i, param in enumerate(params):
                param = all_params[param.base_name]
                param_dict.update({param.base_name + f'_{i}': param})

            # This dictionary allows for easy registration of Qiime parameters
            param_name_to_type_dict = \
                {name: value.type for name, value in param_dict.items()}

            rewrite_function_signature(sig.template,
                                       {},
                                       param_name_to_type_dict,
                                       sig.num_outputs,
                                       action_name)

            outputs = []
            for i in range(sig.num_outputs):
                outputs.append((f'output_{i + 1}', EchoOutput))

            chosen_param_values = {}
            for index, name in enumerate(param_dict):
                if len(param_dict[name].domain) >= sig.num_outputs:
                    chosen_param_values.update(
                        {name: param_dict[name].domain[sig.num_outputs - 1]})
                else:
                    chosen_param_values.update(
                        {name: param_dict[name].domain[0]})

            usage_example = \
                {action_name:
                 UsageInstantiator(chosen_param_values, outputs, action_name)}

            plugin.methods.register_function(
                function=sig.template,
                inputs={},
                parameters=param_name_to_type_dict,
                outputs=outputs,
                name=action_name,
                description='',
                examples=usage_example
            )

            num_functions += 1

plugin.register_formats(EchoOutputFmt, EchoOutputDirFmt)
plugin.register_semantic_types(EchoOutput)
plugin.register_semantic_type_to_format(EchoOutput, EchoOutputDirFmt)
