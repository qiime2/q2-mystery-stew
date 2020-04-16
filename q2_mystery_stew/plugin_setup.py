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

        for name, arg in self.inputs_params.items():
            if 'md' in name:
                arg = arg.to_dataframe()
            elif type(arg) == list or type(arg) == set:
                arg_str = ''
                for val in arg:
                    arg_str += f': {val}'

                arg = arg_str

            param = f'{name}: {arg}\n'

            output1 = use.get_result('output_1')
            output1.assert_has_line_matching(
                label='validate inputs and params',
                path='echo.txt',
                expression=f'{param}',
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
    for num_inputs in range(1, len(function_templates) + 1):
        for num_outputs in range(1, len(function_templates) + 1):
            yield Sig(num_inputs, num_outputs,
                      function_templates[num_outputs - 1])


int_params = {
    # int parameters
    'single_int': Param('single_int',
                        Int, (-1, 0, 1)),
    'int_range_1_param': Param('int_range_1_param',
                               Int % Range(3), (-42, 0, 2)),
    'int_range_1_param_i_e': Param('int_range_1_param_i_e',
                                   Int % Range(3, inclusive_end=True),
                                   (-43, 0, 3)),
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
                                         (-2, 0, 4))
}
int_values = tuple(int_params.values())

float_params = {
    # float parameters
    'single_float': Param('single_float',
                          Float, (-1.5, 0.0, 1.5)),
    'float_range_1_param': Param('float_range_1_param',
                                 Float % Range(2.5), (-42.5, 0.0, 2.49)),
    'float_range_1_param_i_e': Param('float_range_1_param_i_e',
                                     Float % Range(2.5, inclusive_end=True),
                                     (-42.5, 0.0, 2.5)),
    'float_range_2_params': Param('float_range_2_params',
                                  Float % Range(-3.5, 3.5), (-3.5, 0.0, 3.49)),
    'float_range_2_params_i_e': Param('float_range_2_params_i_e',
                                      Float % Range(-3.5, 3.5,
                                                    inclusive_end=True),
                                      (-3.5, 0.0, 3.5)),
    'float_range_2_params_no_i': Param('float_range_2_params_no_i',
                                       Float % Range(-3.5, 3.5,
                                                     inclusive_start=False),
                                       (-3.49, 0.0, 3.49)),
    'float_range_2_params_i_e_ex_s': Param('float_range_2_params_i_e_ex_s',
                                           Float % Range(-3.5, 3.5,
                                                         inclusive_start=False,
                                                         inclusive_end=True),
                                           (-3.49, 0.0, 3.49))
}
float_values = tuple(float_params.values())

collection_params = {
    # collection parameters
    'int_list': Param('int_list', List[Int], (int_values)),
    'float_list': Param('float_list', List[Float], (float_values)),
    'int_set': Param('int_set', Set[Int], (int_values)),
    'float_set': Param('float_set', Set[Float], (float_values))
}

# TODO: What edge cases are there here if any
# Look at helpers (filter_columns, etc.) to try to determine egde cases
mdc_cat_val = pd.Series({'a': 'a'}, name='cat')
mdc_cat_val.index.name = 'id'

mdc_num_val = pd.Series({'a': 1}, name='num')
mdc_num_val.index.name = 'id'

all_params = {
    **int_params,
    **float_params,
    **collection_params,
    # non-numerical parameters
    'string': Param('string',
                    Str, ('', 'some string')),
    'string_choices': Param('string_choices',
                            Str % Choices('A', 'B'), ('A', 'B')),
    'boolean': Param('boolean',
                     Bool, (True, False)),
    'boolean_true': Param('boolean_true',
                          Bool % Choices(True), (True,)),
    'boolean_false': Param('boolean_false',
                           Bool % Choices(False), (False,)),
    'boolean_choice': Param('boolean_choice',
                            Bool % Choices(True, False), (True, False)),
    # metadata parameters
    'md': Param('md', Metadata, (qiime2.Metadata(pd.DataFrame({'a': '1'},
                                 index=pd.Index(['0'], name='id'))),)),
    'mdc_cat': Param('mdc_cat', MetadataColumn[Categorical],
                     (qiime2.CategoricalMetadataColumn(mdc_cat_val),)),
    'mdc_num': Param('mdc_num', MetadataColumn[Numeric],
                     (qiime2.NumericMetadataColumn(mdc_num_val),))
}


def register_test_cases(plugin, all_params):
    num_functions = 0
    signatures = generate_signatures()

    for sig in signatures:
        for params in product(all_params.values(), repeat=sig.num_inputs):
            action_name = f'func_{num_functions}'

            param_dict = {}
            for i, param in enumerate(params):
                param = all_params[param.base_name]
                param_dict.update({param.base_name + f'_{i}': param})

            chosen_param_values = {}
            removed_names = []
            # Collection params come in without a fully specified type
            completed_collection_params = {}
            for index, (name, value) in enumerate(param_dict.items()):
                if value.type == List[Int] or value.type == List[Float]:
                    selected_value = value.domain[num_functions %
                                                  len(value.domain)]
                    selected_name = selected_value.base_name + '_' + name
                    selected_type = List[selected_value.type]
                    new_param = Param(name, selected_type,
                                      selected_value.domain)

                    param_val = []
                    for val in range(sig.num_outputs):
                        selected_size = len(selected_value.domain)
                        param_val.append(
                            selected_value.domain[selected_size %
                                                  sig.num_outputs])

                    removed_names.append(name)
                    completed_collection_params[selected_name] = new_param

                    chosen_param_values.update({selected_name: param_val})
                elif value.type == Set[Int] or value.type == Set[Float]:
                    selected_value = value.domain[num_functions %
                                                  len(value.domain)]
                    selected_name = selected_value.base_name + '_' + name
                    selected_type = Set[selected_value.type]
                    new_param = Param(name, selected_type,
                                      selected_value.domain)

                    param_val = set()
                    for val in range(sig.num_outputs):
                        selected_size = len(selected_value.domain)
                        param_val.add(
                            selected_value.domain[selected_size %
                                                  sig.num_outputs])

                    removed_names.append(name)
                    completed_collection_params[selected_name] = new_param

                    chosen_param_values.update({selected_name: param_val})
                else:
                    domain_size = len(value.domain)
                    chosen_param_values.update(
                        {name: value.domain[sig.num_outputs % domain_size]})

            for name in removed_names:
                param_dict.pop(name)
            param_dict.update(completed_collection_params)

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

            usage_example = \
                {action_name: UsageInstantiator(chosen_param_values, outputs,
                                                action_name)}

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


register_test_cases(plugin, all_params)

plugin.register_formats(EchoOutputFmt, EchoOutputDirFmt)
plugin.register_semantic_types(EchoOutput)
plugin.register_semantic_type_to_format(EchoOutput, EchoOutputDirFmt)
