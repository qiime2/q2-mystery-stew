# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from itertools import product, chain, combinations
from collections import namedtuple
from random import randint

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

Sig = namedtuple('Sig', ['num_params', 'num_outputs', 'template'])
Param = namedtuple('Param', ['base_name', 'qiime_type', 'view_type', 'domain'])
Input = namedtuple('Input', ['base_name', 'qiime_type', 'view_type', 'domain'])

function_templates = (function_template_1output,
                      function_template_2output,
                      function_template_3output)


def create_plugin(ints=False, floats=False, collections=False, strings=False,
                  bools=False, cat_cols=False, num_cols=False, mds=False):
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

    selected_types = []

    if ints:
        selected_types.append(int_params())

    if floats:
        selected_types.append(float_params())

    if collections:
        if ints:
            selected_types.append(list_params(int_params()))
            selected_types.append(set_params(int_params()))

    if strings:
        selected_types.append(string_params())

    if bools:
        selected_types.append(bool_params())

    if cat_cols:
        selected_types.append(cat_col_params())

    if num_cols:
        selected_types.append(num_col_params())

    if mds:
        selected_types.append(md_params())

    if not selected_types:
        raise ValueError("Must select at least one parameter type to use")

    # # itertools.chain didn't produce the results I wanted, so I made this. I
    # # want the result of the chaining to still be a generator
    # # instantiate generators first to solve above
    # def chain_generators():
    #     for type in selected_types:
    #         yield from type()

    register_triple_tests(plugin, chain.from_iterable(selected_types))

    return plugin


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

            param = f'{name}: {arg}'

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
    for num_params in range(1, 4):
        for num_outputs in range(1, len(function_templates) + 1):
            yield Sig(num_params, num_outputs,
                      function_templates[num_outputs - 1])


def generate_simple_signatures():
    yield Sig(1, 1, function_template_1output)


def int_params():
    yield Param('single_int', Int, int, (-1, 0, 1))
    yield Param('int_range_1_param', Int % Range(3), int, (-42, 0, 2))
    yield Param('int_range_1_param_i_e', Int % Range(3, inclusive_end=True),
                int, (-43, 0, 3))
    yield Param('int_range_2_params', Int % Range(-3, 4), int, (-3, 0, 3))
    yield Param('int_range_2_params_i_e',
                Int % Range(-3, 4, inclusive_end=True), int, (-3, 0, 4))
    yield Param('int_range_2_params_no_i',
                Int % Range(-3, 4, inclusive_start=False), int, (-2, 0, 3))
    yield Param('int_range_2_params_i_e_ex_s',
                Int % Range(-3, 4, inclusive_start=False, inclusive_end=True),
                int, (-2, 0, 4))


def float_params():
    yield Param('single_float', Float, float, (-1.5, 0.0, 1.5))
    yield Param('float_range_1_param', Float % Range(2.5), float,
                (-42.5, 0.0, 2.49))
    yield Param('float_range_1_param_i_e',
                Float % Range(2.5, inclusive_end=True), float,
                (-42.5, 0.0, 2.5))
    yield Param('float_range_2_params', Float % Range(-3.5, 3.5), float,
                (-3.5, 0.0, 3.49))
    yield Param('float_range_2_params_i_e',
                Float % Range(-3.5, 3.5, inclusive_end=True), float,
                (-3.5, 0.0, 3.5))
    yield Param('float_range_2_params_no_i',
                Float % Range(-3.5, 3.5, inclusive_start=False), float,
                (-3.49, 0.0, 3.49))
    yield Param('float_range_2_params_i_e_ex_s',
                Float % Range(-3.5, 3.5, inclusive_start=False,
                              inclusive_end=True),
                float, (-3.49, 0.0, 3.49))


def nonull_powerset(iterable):
    "powerset([1,2,3]) --> (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))


def list_params(generator):
    for param in generator:
        yield Param(
            param.base_name + "_list",
            List[param.qiime_type],
            param.view_type,
            tuple(list(x) for x in nonull_powerset(param.domain)))


def set_params(generator):
    for param in generator:
        yield Param(
            param.base_name + "_set",
            Set[param.qiime_type],
            param.view_type,
            tuple(set(x) for x in nonull_powerset(param.domain)))


def collection_params():
    # collection parameters
    params = [Param('int_list', List[Int], (int_params)),
              Param('float_list', List[Float], (float_params)),
              Param('int_set', Set[Int], (int_params)),
              Param('float_set', Set[Float], (float_params))]

    for param in params:
        if param.type == List[Int] or param.type == List[Float]:
            for selected_value in param.domain():
                selected_name = selected_value.base_name + '_' + \
                    param.base_name
                selected_type = List[selected_value.type]
                new_param = Param(param.base_name, selected_type,
                                  selected_value.domain)

                param_val = []
            for _ in range(randint(1, 3)):
                selected_size = len(selected_value.domain)
                param_val.append(
                    selected_value.domain[selected_size %
                                          randint(1, 3)])

        elif param.type == Set[Int] or param.type == Set[Float]:
            for selected_value in param.domain():
                selected_name = selected_value.base_name + '_' + \
                    param.base_name
                selected_type = Set[selected_value.type]
                new_param = Param(param.base_name, selected_type,
                                  selected_value.domain)

                param_val = set()
            for _ in range(randint(1, 3)):
                selected_size = len(selected_value.domain)
                param_val.add(
                    selected_value.domain[selected_size %
                                          randint(1, 3)])

        yield {selected_name: new_param}, {selected_name: param_val}


def string_params():
    yield Param('string', Str, str, ('', 'some string'))
    yield Param('string_choices', Str % Choices('A', 'B'), str, ('A', 'B'))


def bool_params():
    yield Param('boolean',
                Bool, bool, (True, False))
    yield Param('boolean_true',
                Bool % Choices(True), bool, (True,))
    yield Param('boolean_false',
                Bool % Choices(False), bool, (False,))
    yield Param('boolean_choice',
                Bool % Choices(True, False), bool, (True, False))


mdc_cat_val = pd.Series(['a'], index=['a'], name='cat')
mdc_cat_val.index.name = 'id'

mdc_cat_val_nan = pd.Series(['a', np.nan], index=['a', 'b'], name='cat')
mdc_cat_val_nan.index.name = 'id'


def cat_col_params():
    yield Param('mdc_cat', MetadataColumn[Categorical], pd.Series,
                (qiime2.CategoricalMetadataColumn(mdc_cat_val),
                 qiime2.CategoricalMetadataColumn(mdc_cat_val_nan)))


mdc_num_val = pd.Series([1], index=['a'], name='num')
mdc_num_val.index.name = 'id'

mdc_num_val_nan = pd.Series([1, np.nan], index=['a', 'b'], name='num')
mdc_num_val_nan.index.name = 'id'

mdc_num_nan = pd.Series([np.nan], index=['a'], name='num')
mdc_num_nan.index.name = 'id'


def num_col_params():
    yield Param('mdc_num', MetadataColumn[Numeric], pd.Series,
                (qiime2.NumericMetadataColumn(mdc_num_val),
                 qiime2.NumericMetadataColumn(mdc_num_val_nan),
                 qiime2.NumericMetadataColumn(mdc_num_nan)))


def md_params():
    yield Param('md', Metadata, pd.DataFrame,
                (qiime2.Metadata(pd.DataFrame({'a': '1'}, index=pd.Index(['0'],
                                 name='id'))),
                 qiime2.Metadata(pd.DataFrame({'a': '1'},
                                 index=pd.Index(['0', '1'], name='id'))),
                 qiime2.Metadata(pd.DataFrame({}, index=pd.Index(['0'],
                                 name='id'))),))


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


def register_single_tests(plugin, selected_params):
    for idx, param in enumerate(selected_params):
        action_name = f'func_single_{idx}'
        param_annotations = {param.base_name: param.view_type}
        qiime_annotations = {param.base_name: param.qiime_type}
        func = function_template_1output

        rewrite_function_signature(func, {}, param_annotations, 1, action_name)
        outputs = [('output_1', EchoOutput)]
        usage_example = {
            f'example_{i}': UsageInstantiator(
                {}, {param.base_name: val}, outputs, action_name)
            for i, val in enumerate(param.domain)
        }

        plugin.methods.register_function(
            function=func,
            inputs={},
            parameters=qiime_annotations,
            outputs=outputs,
            name=action_name,
            description='',
            examples=usage_example
        )


def register_double_tests(plugin, selected_params):
    for idx, params in enumerate(product(selected_params, repeat=2)):
        action_name = f'func_double_{idx}'
        param_annotations = \
            {param.base_name: param.view_type for param in params}
        qiime_annotations = \
            {param.base_name: param.qiime_type for param in params}
        func = function_template_1output

        param_name1 = params[0].base_name
        param_name2 = params[1].base_name
        params = product(params[0].domain, params[1].domain)
        rewrite_function_signature(func, {}, param_annotations, 1, action_name)
        outputs = [('output_1', EchoOutput)]
        usage_example = {
            f'example_{i}': UsageInstantiator(
                {}, {param_name1: val1, param_name2: val2},
                outputs, action_name) for i, (val1, val2) in enumerate(params)
        }

        plugin.methods.register_function(
            function=func,
            inputs={},
            parameters=qiime_annotations,
            outputs=outputs,
            name=action_name,
            description='',
            examples=usage_example
        )


def register_triple_tests(plugin, selected_params):
    for idx, params in enumerate(product(selected_params, repeat=3)):
        action_name = f'func_triple_{idx}'
        param_annotations = \
            {param.base_name: param.view_type for param in params}
        qiime_annotations = \
            {param.base_name: param.qiime_type for param in params}
        func = function_template_1output

        param_name1 = params[0].base_name
        param_name2 = params[1].base_name
        param_name3 = params[2].base_name
        params = product(params[0].domain, params[1].domain, params[2].domain)
        rewrite_function_signature(func, {}, param_annotations, 1, action_name)
        outputs = [('output_1', EchoOutput)]
        usage_example = {
            f'example_{i}': UsageInstantiator(
                {}, {param_name1: val1, param_name2: val2, param_name3: val3},
                outputs, action_name) for i, (val1, val2,
                                              val3) in enumerate(params)
        }

        plugin.methods.register_function(
            function=func,
            inputs={},
            parameters=qiime_annotations,
            outputs=outputs,
            name=action_name,
            description='',
            examples=usage_example
        )


# Selecting a value via the usage of `length(iterable) % some_value` as an
# index allows for a fairly arbitrary selection of a value without resorting to
# any form of randomization
def register_test_cases(plugin, selected_params):
    num_functions = 0
    signatures = generate_signatures()

    for sig in signatures:
        for params in product(selected_params(), repeat=sig.num_params):
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
            chosen_param_values = {}
            for i, param in enumerate(params):
                if type(param) == tuple:
                    param_dict.update(param[0])
                    chosen_param_values.update(param[1])
                else:
                    name = param.base_name + f'_{i}'
                    param_dict.update({name: param})
                    domain_size = len(param.domain)
                    chosen_param_values.update(
                        {name: param.domain[sig.num_outputs % domain_size]})

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
