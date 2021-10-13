# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from inspect import Parameter

from qiime2.plugin import Plugin
from qiime2.sdk.util import is_semantic_type

import q2_mystery_stew
from q2_mystery_stew.type import (EchoOutput, SingleInt1, SingleInt2,
                                  IntWrapper, WrappedInt1, WrappedInt2,
                                  EchoOutputBranch1, EchoOutputBranch2,
                                  EchoOutputBranch3)
from q2_mystery_stew.usage import UsageInstantiator
from q2_mystery_stew.format import (SingleIntFormat, SingleIntDirectoryFormat,
                                    EchoOutputFmt, EchoOutputDirFmt)
from q2_mystery_stew.template import get_disguised_echo_function
from q2_mystery_stew.generators import (
        get_param_generators, generate_single_type_methods)
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
    for generator in selected_types:
        for action_template in generate_single_type_methods(generator):
            register_test_method(plugin, action_template)

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

    plugin.register_semantic_type_to_format(
        EchoOutput | EchoOutputBranch1 | EchoOutputBranch2 | EchoOutputBranch3,
        EchoOutputDirFmt)

    plugin.register_transformer(to_single_int_format)


def register_test_method(plugin, action_template):
    qiime_inputs = {}
    qiime_parameters = {}
    qiime_outputs = action_template.registered_outputs

    python_parameters = []
    for spec in action_template.parameter_specs.values():
        print(spec.default)
        python_parameters.append(Parameter(spec.name,
                                           Parameter.POSITIONAL_OR_KEYWORD,
                                           annotation=spec.view_type,
                                           default=spec.default))
        if is_semantic_type(spec.qiime_type):
            qiime_inputs[spec.name] = spec.qiime_type
        else:
            qiime_parameters[spec.name] = spec.qiime_type

    function = get_disguised_echo_function(id=action_template.action_id,
                                           python_parameters=python_parameters,
                                           num_outputs=len(qiime_outputs))
    usage_examples = {}
    for idx, invocation in enumerate(action_template.invocation_domain):
        usage_examples[f'example_{idx}'] = UsageInstantiator(
            id=action_template.action_id,
            parameter_specs=action_template.parameter_specs,
            arguments=invocation.kwargs,
            expected_outputs=invocation.expected_output_types
        )

    plugin.methods.register_function(
        function=function,
        inputs=qiime_inputs,
        parameters=qiime_parameters,
        outputs=qiime_outputs,
        input_descriptions={},
        parameter_descriptions={},
        output_descriptions={},
        name=action_template.action_id.replace("_", "-"),
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
