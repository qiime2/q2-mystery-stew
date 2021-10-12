# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import re
from itertools import chain

from qiime2.sdk.util import (is_semantic_type, is_metadata_type,
                             is_metadata_column_type)

from q2_mystery_stew.template import argument_to_line


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
                if type(argument) == list or type(argument) == set:
                    collection_type = type(argument)
                    transformed_inputs[name] = collection_type()
                    inputs[name] = collection_type()

                    for arg in argument:
                        artifact = arg()
                        view = artifact.view(template.view_type)
                        view.__hide_from_garbage_collector = artifact

                        if collection_type == list:
                            transformed_inputs[name].append(view)
                            inputs[name].append(
                                use.init_artifact(arg.__name__, arg))
                        elif collection_type == set:
                            transformed_inputs[name].add(view)
                            inputs[name].add(
                                use.init_artifact(arg.__name__, arg))
                else:
                    inputs[name] = use.init_artifact(argument.__name__,
                                                     argument)
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
                    inputs[name] = use.get_metadata_column(
                        '%s_%s' % (factory.__name__, column_name),
                        column_name,
                        md_rec,
                    )
                    transformed_inputs[name] = md.get_column(column_name)

            else:
                inputs[name] = transformed_inputs[name] = argument

        computed_results = use.action(
            use.UsageAction(plugin_id='mystery_stew', action_id=self.name),
            use.UsageInputs(**inputs),
            use.UsageOutputNames(**self.output_names),
        )

        for idx, (output_name, expected_type) in enumerate(self.outputs):
            self._assert_output(computed_results, transformed_inputs,
                                self.defaults, output_name, expected_type, idx)

    @staticmethod
    def _fmt_regex(name, arg):
        line = argument_to_line(name, arg).strip()
        return re.escape(line)

    def _assert_output(self, computed_results, inputs, defaults, output_name,
                       expected_type, idx):
        output = computed_results[idx]
        if idx == 0:
            for input_name, input_arg in chain(inputs.items(),
                                               defaults.items()):
                regex = self._fmt_regex(input_name, input_arg)
                output.assert_has_line_matching(
                    label='<generated>',
                    path='echo.txt',
                    expression=regex
                )
        else:
            output.assert_has_line_matching(
                label='<generated>',
                path='echo.txt',
                expression=str(idx),
            )
