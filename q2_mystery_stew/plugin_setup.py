# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from itertools import product, chain
from collections import namedtuple
import pandas as pd
import numpy as np

import qiime2
from qiime2.plugin import (Plugin, Int, Range, Float, Bool, Str, Choices,
                           List, Set, Metadata, MetadataColumn, Categorical,
                           Numeric, UsageAction, UsageInputs,
                           UsageOutputNames, Properties)

import q2_mystery_stew
from .type import (SingleInt1, SingleInt2, IntWrapper,
                   WrappedInt1, WrappedInt2)
from .format import SingleIntFormat, SingleIntDirectoryFormat
from q2_mystery_stew.template import (rewrite_function_signature,
                                      function_template_1output,
                                      function_template_2output,
                                      function_template_3output)
from q2_mystery_stew.templatable_echo_fmt import (EchoOutput, EchoOutputFmt,
                                                  EchoOutputDirFmt)


def create_plugin():
    plugin = Plugin(
               name='mystery-stew',
               project_name='q2-mystery-stew',
               version=q2_mystery_stew.__version__,
               website='https://github.com/qiime2/q2-mystery-stew',
               package='q2_mystery_stew',
               description=('This QIIME 2 plugin templates out arbitrary '
                            'QIIME 2 actions to test interfaces. '),
               short_description='Plugin for generating arbitrary QIIME 2 '
                                 'actions.'
             )

    plugin.register_semantic_types(SingleInt1, SingleInt2, IntWrapper,
                                   WrappedInt1, WrappedInt2, EchoOutput)

    plugin.register_formats(SingleIntFormat, SingleIntDirectoryFormat,
                            EchoOutputFmt, EchoOutputDirFmt)

    plugin.register_semantic_type_to_format(SingleInt1,
                                            SingleIntDirectoryFormat)
    plugin.register_semantic_type_to_format(SingleInt2,
                                            SingleIntDirectoryFormat)

    plugin.register_semantic_type_to_format(
        IntWrapper[WrappedInt1 | WrappedInt2], SingleIntDirectoryFormat)

    plugin.register_semantic_type_to_format(EchoOutput, EchoOutputDirFmt)

    # This transformer is being registered in this file right now because it is
    # needed by `register_test_cases` so it needs to be registered before it is
    # called
    @plugin.register_transformer
    def _0(data: int) -> SingleIntFormat:
        ff = SingleIntFormat()
        with ff.open() as fh:
            fh.write('%d\n' % data)
        return ff

    register_test_cases(plugin, inputs, all_params)

    return plugin


Sig = namedtuple('Sig', ['num_params', 'num_outputs', 'template'])
Param = namedtuple('Param', ['base_name', 'type', 'domain'])
Input = namedtuple('Input', ['base_name', 'qiime_type', 'format', 'domain'])

function_templates = (function_template_1output,
                      function_template_2output,
                      function_template_3output)


class UsageInstantiator:
    def __init__(self, inputs, params, outputs, name):
        self.inputs = inputs
        self.params = params
        self.outputs = outputs
        self.name = name
        self.output_names = {k: k for k, _ in self.outputs}

        # This is a bit of a hack. I don't want to explicitly use IntWrapper
        # because I want the implementation to be extensible, but when I got
        # the name of the wrapper type and parsed it to a qiime type it gave me
        # a complete TypeExp which didn't allow me to set what inner type I
        # wanted. So any types that may be encountered with a union as a field
        # must be in this dict
        self.types = {'IntWrapper': IntWrapper}

    def __call__(self, use):
        inputs = {}
        for name, input_ in self.inputs.items():
            if qiime2.core.type.is_union(input_.qiime_type):
                union = input_.qiime_type.unpack_union()
                types = [type_ for type_ in union]

                type_ = types[len(self.inputs) % len(types)]
            elif len(input_.qiime_type.fields) > 0 and \
                    qiime2.core.type.is_union(input_.qiime_type.fields[0]):
                outter_type = self.types[input_.qiime_type.name]

                union = input_.qiime_type.fields[0].unpack_union()
                types = [type_ for type_ in union]

                inner_type = types[len(self.inputs) % len(types)]
                type_ = outter_type[inner_type]
            else:
                type_ = input_.qiime_type

            value = input_.domain[len(self.outputs) % len(input_.domain)]
            inputs[name] = factory(type_, value)

        use.action(
            UsageAction(plugin_id='mystery_stew', action_id=self.name),
            UsageInputs(**inputs, **self.params),
            UsageOutputNames(**self.output_names),
        )

        for name, arg in chain(inputs.items(), self.params.items()):
            if 'md' in name:
                arg = arg.to_dataframe()
                arg = str(arg)
                arg = arg.replace('[', ':').replace(']', ':')
            elif type(arg) == list or type(arg) == set:
                arg_str = ''
                for val in arg:
                    arg_str += f': {val}'

                arg = arg_str
            elif type(arg) == qiime2.sdk.result.Artifact:
                arg = arg.uuid

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
    for num_params in range(1, len(function_templates) + 1):
        for num_outputs in range(1, len(function_templates) + 1):
            yield Sig(num_params, num_outputs,
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

mdc_cat_val = pd.Series(['a'], index=['a'], name='cat')
mdc_cat_val.index.name = 'id'

mdc_cat_val_nan = pd.Series(['a', np.nan], index=['a', 'b'], name='cat')
mdc_cat_val_nan.index.name = 'id'

mdc_num_val = pd.Series([1], index=['a'], name='num')
mdc_num_val.index.name = 'id'

mdc_num_val_nan = pd.Series([1, np.nan], index=['a', 'b'], name='num')
mdc_num_val_nan.index.name = 'id'

mdc_num_nan = pd.Series([np.nan], index=['a'], name='num')
mdc_num_nan.index.name = 'id'

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
                                                 index=pd.Index(['0'],
                                                 name='id'))),
                                 qiime2.Metadata(pd.DataFrame({'a': '1'},
                                                 index=pd.Index(['0', '1'],
                                                 name='id'))),
                                 qiime2.Metadata(pd.DataFrame({},
                                                 index=pd.Index(['0'],
                                                 name='id'))),)),
    'mdc_cat': Param('mdc_cat', MetadataColumn[Categorical],
                     (qiime2.CategoricalMetadataColumn(mdc_cat_val),
                      qiime2.CategoricalMetadataColumn(mdc_cat_val_nan),)),
    'mdc_num': Param('mdc_num', MetadataColumn[Numeric],
                     (qiime2.NumericMetadataColumn(mdc_num_val),
                      qiime2.NumericMetadataColumn(mdc_num_val_nan),
                      qiime2.NumericMetadataColumn(mdc_num_nan))),
}

inputs = (
    Input('SingleInt1', SingleInt1, SingleIntFormat, (-1, 0, 1)),
    Input('SingleIntProperty', SingleInt1 % Properties('A'),
          SingleIntFormat, (-1, 0, 1)),
    Input('SingleIntPropertyExclude', SingleInt1 % Properties(exclude=('A')),
          SingleIntFormat, (1, -1, -0)),
    Input('SingleInt1USingleInt2', SingleInt1 | SingleInt2, SingleIntFormat,
          (1, -1, 0)),
    Input('WrappedInt', IntWrapper[WrappedInt1], SingleIntFormat, (0, 1, -1)),
    Input('WrappedUnion', IntWrapper[WrappedInt1 | WrappedInt2],
          SingleIntFormat, (-1, 0, 1)),
)


def factory(format_, value):
    return qiime2.Artifact.import_data(format_, value)


# Selecting a value via the usage of `length(iterable) % some_value` as an
# index allows for a fairly arbitrary selection of a value without resorting to
# any form of randomization
def register_test_cases(plugin, input, all_params):
    num_functions = 0
    signatures = generate_signatures()

    for sig in signatures:
        for params in product(all_params.values(), repeat=sig.num_params):
            action_name = f'func_{num_functions}'

            input_name_to_type_dict = {}
            input_name_to_format_dict = {}
            input_name_to_named_tuple_dict = {}
            num_inputs = (num_functions % 3) + 1
            for input_num in range(num_inputs):
                if input_num == 0:
                    input_index = num_functions % len(inputs)
                elif input_num == 1:
                    input_index = (num_functions + num_inputs) % len(inputs)
                elif input_num == 2:
                    input_index = \
                        (num_functions + sig.num_params) % len(inputs)

                input_ = inputs[input_index]
                name = input_.base_name + f'_{input_num}'

                input_name_to_type_dict.update({name: input_.qiime_type})
                input_name_to_format_dict.update({name: input_.format})
                input_name_to_named_tuple_dict.update({name: input_})

            param_dict = {}
            for i, param in enumerate(params):
                param = all_params[param.base_name]
                param_dict.update({param.base_name + f'_{i}': param})

            chosen_param_values = {}
            removed_names = []
            # Collection params come in without a fully specified type, they
            # know they are a List or a Set of Ints or Floats, but they don't
            # yet know what types of Ints or Floats they are going to be
            # composed of
            completed_collection_params = {}
            for (name, value) in param_dict.items():
                if value.type == List[Int] or value.type == List[Float]:
                    selected_value = value.domain[num_functions %
                                                  len(value.domain)]
                    selected_name = selected_value.base_name + '_' + name
                    selected_type = List[selected_value.type]
                    new_param = Param(name, selected_type,
                                      selected_value.domain)

                    param_val = []
                    for _ in range(sig.num_outputs):
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
                                       input_name_to_format_dict,
                                       param_name_to_type_dict,
                                       sig.num_outputs,
                                       action_name)

            outputs = []
            for i in range(sig.num_outputs):
                outputs.append((f'output_{i + 1}', EchoOutput))

            usage_example = \
                {action_name: UsageInstantiator(input_name_to_named_tuple_dict,
                                                chosen_param_values, outputs,
                                                action_name)}

            plugin.methods.register_function(
                function=sig.template,
                inputs=input_name_to_type_dict,
                parameters=param_name_to_type_dict,
                outputs=outputs,
                name=action_name,
                description='',
                examples=usage_example
            )

            num_functions += 1
