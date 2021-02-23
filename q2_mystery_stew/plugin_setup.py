# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from itertools import product, chain, combinations
from collections import namedtuple, deque
from random import randint
import re
from inspect import Parameter

import pandas as pd
import numpy as np

import qiime2
from qiime2.core.type.util import is_metadata_column_type, is_metadata_type
from qiime2.plugin import (Plugin, Int, Range, Float, Bool, Str, Choices,
                           List, Set, Metadata, MetadataColumn, Categorical,
                           Numeric, Properties)
from qiime2.sdk.util import is_semantic_type

import q2_mystery_stew
from .type import (SingleInt1, SingleInt2, IntWrapper,
                   WrappedInt1, WrappedInt2)
from .format import SingleIntFormat, SingleIntDirectoryFormat
from .util import reservoir_sampler
from q2_mystery_stew.template import (rewrite_function_signature,
                                      function_template_1output,
                                      function_template_2output,
                                      function_template_3output,
                                      argument_to_line, disguise_function)
from q2_mystery_stew.templatable_echo_fmt import (EchoOutput, EchoOutputFmt,
                                                  EchoOutputDirFmt)

ParamTemplate = namedtuple('ParamTemplate', ['base_name', 'qiime_type',
                                             'view_type', 'domain'])

function_templates = (function_template_1output,
                      function_template_2output,
                      function_template_3output)


def create_plugin(**filters):
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
    # needed by the registration functions so it needs to be registered before
    # it is called
    @plugin.register_transformer
    def _0(data: int) -> SingleIntFormat:
        ff = SingleIntFormat()
        with ff.open() as fh:
            fh.write('%d\n' % data)
        return ff

    selected_types = []
    basics = {
        'ints': int_params,
        'floats': float_params,
        'strings': string_params,
        'bools': bool_params,
        'metadata': simple_metadata,
        'primitive_unions': primitive_unions,
        'artifacts': artifact_params
    }

    for key, generator in basics.items():
        if not filters or filters.get(key, False):
            selected_types.append(generator())
            if not filters or filters.get('collections', False):
                selected_types.append(list_params(generator()))
                selected_types.append(set_params(generator()))

    if not selected_types:
        raise ValueError("Must select at least one parameter type to use")

    register_single_type_tests(plugin, selected_types)

    return plugin


class UsageInstantiator:
    def __init__(self, name, param_templates, inputs, outputs, defaults=None):
        self.name = name
        self.param_templates = param_templates
        self.inputs = inputs
        self.outputs = outputs
        if defaults is None:
            defaults = {}
        self.defaults = defaults
        self.output_names = {k: k for k, _ in self.outputs}

    def __call__(self, use):
        inputs = {}
        transformed_inputs = {}

        for name, argument in self.inputs.items():
            template = self.param_templates[name]

            if argument is None:
                inputs[name] = transformed_inputs[name] = None
            elif is_semantic_type(template.qiime_type):
                inputs[name] = use.init_data(argument.__name__, argument)
                artifact = argument()
                view = artifact.view(template.view_type)
                view.__hide_from_garbage_collector = artifact
                transformed_inputs[name] = view
            elif is_metadata_type(template.qiime_type):
                if is_metadata_column_type(template.qiime_type):
                    factory, column_name = argument
                else:
                    factory, column_name = argument, None

                md_rec = use.init_metadata(factory.__name__, factory)
                md = factory()

                if column_name is None:
                    inputs[name] = md_rec
                    transformed_inputs[name] = md
                else:
                    inputs[name] = use.get_metadata_column(column_name, md_rec)
                    transformed_inputs[name] = md.get_column(column_name)

            else:
                inputs[name] = transformed_inputs[name] = argument

        use.action(
            use.UsageAction(plugin_id='mystery_stew', action_id=self.name),
            use.UsageInputs(**inputs),
            use.UsageOutputNames(**self.output_names),
        )

        for idx, (output_name, expected_type) in enumerate(self.outputs):
            self._assert_output(use, transformed_inputs, self.defaults,
                                output_name, expected_type, idx)

    @staticmethod
    def _fmt_regex(name, arg):
        line = argument_to_line(name, arg).strip()
        return re.escape(line)

    def _assert_output(self, use, inputs, defaults, output_name, expected_type,
                       idx):
        if idx == 0:
            for input_name, input_arg in chain(inputs.items(),
                                               defaults.items()):
                regex = self._fmt_regex(input_name, input_arg)
                output = use.get_result(output_name)
                output.assert_has_line_matching(
                    label='<generated>',
                    path='echo.txt',
                    expression=regex
                )
        else:
            output = use.get_result(output_name)
            output.assert_has_line_matching(
                label='<generated>',
                path='echo.txt',
                expression=str(idx),
            )


def single_int1():
    return qiime2.Artifact.import_data('SingleInt1', 42)

def single_int2():
    return qiime2.Artifact.import_data('SingleInt2', 2019)

def artifact_params():
    yield ParamTemplate('simple_type1', SingleInt1, SingleIntFormat,
                        (single_int1,))
    yield ParamTemplate('simple_type2', SingleInt2, SingleIntFormat,
                        (single_int2,))
    yield ParamTemplate('union_type', SingleInt1 | SingleInt2, SingleIntFormat,
                        (single_int1, single_int2))


def metadata1():
    df = pd.DataFrame({'col1': ['a', 'b', 'c'], 'col2': ['x', 'y', 'z']},
                     index=['id1', 'id2', 'id3'])
    df.index.name = 'id'
    return qiime2.Metadata(df)


def simple_metadata():
    yield ParamTemplate('metadata_cat', Metadata, qiime2.Metadata,
                        (metadata1,))
    yield ParamTemplate('column_cat', MetadataColumn[Categorical],
                        qiime2.CategoricalMetadataColumn,
                        ([metadata1, 'col1'], [metadata1, 'col2']))


def int_params():
    yield ParamTemplate('single_int', Int, int, (-1, 0, 1))
    yield ParamTemplate('int_range_1_param', Int % Range(3), int, (-42, 0, 2))
    yield ParamTemplate('int_range_1_param_i_e',
                        Int % Range(3, inclusive_end=True), int, (-43, 0, 3))
    yield ParamTemplate('int_range_2_params',
                        Int % Range(-3, 4), int, (-3, 0, 3))
    yield ParamTemplate('int_range_2_params_i_e',
                Int % Range(-3, 4, inclusive_end=True), int, (-3, 0, 4))
    yield ParamTemplate('int_range_2_params_no_i',
                Int % Range(-3, 4, inclusive_start=False), int, (-2, 0, 3))
    yield ParamTemplate('int_range_2_params_i_e_ex_s',
                Int % Range(-3, 4, inclusive_start=False, inclusive_end=True),
                int, (-2, 0, 4))


def float_params():
    yield ParamTemplate('single_float', Float, float, (-1.5, 0.0, 1.5))
    yield ParamTemplate('float_range_1_param', Float % Range(2.5), float,
                (-42.5, 0.0, 2.49))
    yield ParamTemplate('float_range_1_param_i_e',
                Float % Range(2.5, inclusive_end=True), float,
                (-42.5, 0.0, 2.5))
    yield ParamTemplate('float_range_2_params', Float % Range(-3.5, 3.5),
                float, (-3.5, 0.0, 3.49))
    yield ParamTemplate('float_range_2_params_i_e',
                Float % Range(-3.5, 3.5, inclusive_end=True), float,
                (-3.5, 0.0, 3.5))
    yield ParamTemplate('float_range_2_params_no_i',
                Float % Range(-3.5, 3.5, inclusive_start=False), float,
                (-3.49, 0.0, 3.49))
    yield ParamTemplate('float_range_2_params_i_e_ex_s',
                Float % Range(-3.5, 3.5, inclusive_start=False,
                              inclusive_end=True),
                float, (-3.49, 0.0, 3.49))


def nonull_powerset(iterable):
    "powerset([1,2,3]) --> (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))


def list_params(generator):
    for param in generator:
        yield ParamTemplate(
            param.base_name + "_list",
            List[param.qiime_type],
            param.view_type,
            tuple(list(x) for x in nonull_powerset(param.domain)))


def set_params(generator):
    for param in generator:
        yield ParamTemplate(
            param.base_name + "_set",
            Set[param.qiime_type],
            param.view_type,
            tuple(set(x) for x in nonull_powerset(param.domain)))


def string_params():
    # TODO: should '' be in this list?
    mean_choices = ('None', '-1', 'True', 'False', '<[^#^]>')
    yield ParamTemplate('string', Str, str, mean_choices)
    yield ParamTemplate('string_choices', Str % Choices(*mean_choices),
                        str, mean_choices)


def bool_params():
    yield ParamTemplate('boolean',
                Bool, bool, (True, False))
    yield ParamTemplate('boolean_true',
                Bool % Choices(True), bool, (True,))
    yield ParamTemplate('boolean_false',
                Bool % Choices(False), bool, (False,))
    yield ParamTemplate('boolean_choice',
                Bool % Choices(True, False), bool, (True, False))


def primitive_unions():
    yield ParamTemplate('disjoint', Int % (Range(5, 10) | Range(15, 20)),
                        int, (5, 9, 15, 19))
    yield ParamTemplate('auto_int',
                        Int % Range(1, None) | Str % Choices('auto'),
                        object, (1, 10, 'auto'))
    yield ParamTemplate('kitchen_sink',
                        Float % Range(0, 1) | Int | Str % Choices('auto', 'Beef') | Bool | Float % Range(10, 11),
                        object, (0.5, 1000, 'Beef', 'auto', True, False, 10.103))


                        #Int % Range(-2, 9) | Str % Choices('auto', 'Beef') | Bool | Int % Range(50, None) | Float % Range(10, 11),

def register_single_type_tests(plugin, list_of_params):
    for generator in list_of_params:
        for idx, param in enumerate(generator, 1):
            action_id = f'test_{generator.__name__}_{idx}'
            function_parameters = []
            qiime_annotations = {}
            defaults = {}

            # Required
            param_name = param.base_name
            function_parameters.append(
                Parameter(param_name, Parameter.POSITIONAL_OR_KEYWORD,
                          annotation=param.view_type))
            qiime_annotations[param_name] = param.qiime_type

            # Optional
            param_name = f'optional_{param.base_name}'
            function_parameters.append(
                Parameter(param_name, Parameter.POSITIONAL_OR_KEYWORD,
                          annotation=param.view_type, default=None))
            qiime_annotations[param_name] = param.qiime_type
            defaults[param_name] = None

            if (not is_semantic_type(param.qiime_type)
                    and not is_metadata_type(param.qiime_type)):
                # Defaults
                for i_, default in enumerate(param.domain, 1):
                    param_name = f'default{i_}_{param.base_name}'
                    function_parameters.append(
                        Parameter(param_name, Parameter.POSITIONAL_OR_KEYWORD,
                                  annotation=param.view_type, default=default))
                    qiime_annotations[param_name] = param.qiime_type
                    defaults[param_name] = default

            func = function_template_1output
            disguise_function(func, action_id, function_parameters, 1)

            qiime_inputs = {}
            qiime_parameters = {}
            qiime_outputs = [('only_output', EchoOutput)]
            for name, val in qiime_annotations.items():
                if is_semantic_type(val):
                    qiime_inputs[name] = val
                else:
                    qiime_parameters[name] = val

            usage_examples = {}
            for i, arg in enumerate(param.domain):
                usage_examples[f'example_{i}'] = UsageInstantiator(
                    action_id, {param.base_name: param},
                    {param.base_name: arg}, qiime_outputs, defaults)

            # one more with defaults all passed a different value
            new_inputs = {
                # the last iteration is fine, we aren't testing this param
                param.base_name: arg
            }
            shifted_args = deque([arg, *param.domain])
            shifted_args.rotate(1)
            for key, arg in zip(defaults, shifted_args):
                new_inputs[key] = arg

            usage_examples[f'example_{i+1}'] = UsageInstantiator(
                action_id,
                {k: param for k in chain([param.base_name], defaults)},
                new_inputs, qiime_outputs)

            # prove we can still pass defaults manually
            usage_examples[f'example_{i+2}'] = UsageInstantiator(
                action_id,
                {k: param for k in chain([param.base_name], defaults)},
                {param.base_name: arg, **defaults}, qiime_outputs)


            plugin.methods.register_function(
                function=func,
                inputs=qiime_inputs,
                parameters=qiime_parameters,
                outputs=qiime_outputs,
                input_descriptions={},
                parameter_descriptions={},
                output_descriptions={},
                name=f'Phrase describing {action_id.replace("_", "-")}',
                description=LOREM_IPSUM,
                examples=usage_examples
            )



# TODO: will this be dead code soon?
def register_tests(plugin, selected_params, signature_size, max_params=None,
                   max_examples=None):
    for idx, params in enumerate(
            reservoir_sampler(combinations(selected_params, signature_size),
                              n=max_params)):
        action_name = f'func_{signature_size}params_{idx}'
        param_annotations = \
            {param.base_name + '_' + str(i): param.view_type for i,
             param in enumerate(params)}
        qiime_annotations = \
            {param.base_name + '_' + str(i): param.qiime_type for i,
             param in enumerate(params)}
        func = function_template_1output

        param_templates = {
            param.base_name + f'_{i}': param for i, param in enumerate(params)}

        args = reservoir_sampler(product(*[param.domain for param in params]),
                                 n=max_examples)
        rewrite_function_signature(func, {}, param_annotations, 1, action_name)
        outputs = [('only_output', EchoOutput)]

        usage_examples = {}
        for i, arg in enumerate(args):
            example_arguments = {
                name: binding for name, binding in zip(param_templates, arg)}
            usage_examples[f'example_{i}'] = UsageInstantiator(
                action_name, param_templates, example_arguments, outputs)

        qiime_inputs = {}
        qiime_parameters = {}
        for name, val in qiime_annotations.items():
            if is_semantic_type(val):
                qiime_inputs[name] = val
            else:
                qiime_parameters[name] = val

        plugin.methods.register_function(
            function=func,
            inputs=qiime_inputs,
            parameters=qiime_parameters,
            outputs=outputs,
            name=f'Short desc: {action_name}',
            description=f'Long desc: {action_name}',
            examples=usage_examples
        )


LOREM_IPSUM = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vel ipsum
justo. Nulla a dolor tincidunt, lacinia libero sed, placerat odio. Vivamus
tempus, sapien at consequat finibus, est libero tempor turpis, vel imperdiet
tortor dui sit amet justo. Aliquam erat volutpat. In sed quam a nisi congue
semper et nec leo. Pellentesque massa eros, finibus ac lacus ac, dignissim
consectetur ipsum. Nullam ac arcu nisi. Etiam nec eros sapien. Nulla malesuada
interdum vulputate. Donec id semper urna.

Proin sagittis lectus scelerisque auctor bibendum. Phasellus aliquet, massa
sit amet vestibulum interdum, nibh ante tempor lorem, quis ornare sem ipsum
nec lacus. Suspendisse id nulla feugiat, euismod ex et, lacinia sem. Ut congue
hendrerit ex imperdiet lobortis. Phasellus auctor sit amet ex euismod
ultricies. Ut ultrices ultrices tempus. Curabitur vitae velit eget nibh
vulputate interdum. Quisque egestas vitae metus vitae lobortis. Sed ullamcorper
ligula eu dignissim ultricies. Donec imperdiet ut ipsum a sagittis.
Donec at mauris velit.
"""