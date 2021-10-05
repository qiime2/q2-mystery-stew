# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from inspect import Parameter
from itertools import chain
from collections import deque

from qiime2.plugin import Plugin
from qiime2.sdk.util import is_metadata_type, is_semantic_type

import q2_mystery_stew
from q2_mystery_stew.type import (EchoOutput, SingleInt1, SingleInt2,
                                  IntWrapper, WrappedInt1, WrappedInt2)
from q2_mystery_stew.usage import UsageInstantiator
from q2_mystery_stew.format import (SingleIntFormat, SingleIntDirectoryFormat,
                                    EchoOutputFmt, EchoOutputDirFmt)
from q2_mystery_stew.template import (function_template_1output,
                                      disguise_function)
from q2_mystery_stew.generators import get_param_generators
from q2_mystery_stew.transformers import to_single_int_format


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

    register_base_implementation(plugin)

    selected_types = get_param_generators(**filters)
    register_single_type_tests(plugin, selected_types)

    return plugin


def register_base_implementation(plugin):
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

    plugin.register_transformer(to_single_int_format)


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
