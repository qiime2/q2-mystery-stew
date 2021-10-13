# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import re

from qiime2.sdk.util import (is_semantic_type, is_metadata_type,
                             is_metadata_column_type)

from q2_mystery_stew.template import argument_to_line


class UsageInstantiator:
    def __init__(self, id, parameter_specs, arguments, expected_outputs):
        self.id = id
        self.parameter_specs = parameter_specs
        self.arguments = arguments
        self.expected_outputs = expected_outputs
        self.output_names = {k: k for k, _ in self.expected_outputs}
        print(parameter_specs)

    def __call__(self, use):
        inputs = {}
        realized_arguments = {}

        for name, argument in self.arguments.items():
            spec = self.parameter_specs[name]

            if argument is None:
                inputs[name] = realized_arguments[name] = None
            elif is_semantic_type(spec.qiime_type):
                if type(argument) == list or type(argument) == set:
                    collection_type = type(argument)
                    input_temp = []
                    realized_arguments[name] = collection_type()

                    for arg in argument:
                        input_temp.append(use.init_data(arg.__name__, arg))
                        artifact = arg()
                        view = artifact.view(spec.view_type)
                        view.__hide_from_garbage_collector = artifact

                        if collection_type == list:
                            realized_arguments[name].append(view)
                        elif collection_type == set:
                            realized_arguments[name].add(view)
                        inputs[name] = \
                            use.init_data_collection(name, collection_type,
                                                     *input_temp)
                else:
                    inputs[name] = use.init_data(argument.__name__, argument)
                    artifact = argument()
                    view = artifact.view(spec.view_type)
                    view.__hide_from_garbage_collector = artifact
                    realized_arguments[name] = view
            elif is_metadata_type(spec.qiime_type):
                if is_metadata_column_type(spec.qiime_type):
                    factory, column_name = argument
                else:
                    factory, column_name = argument, None

                md_rec = use.init_metadata(factory.__name__, factory)
                md = factory()

                if column_name is None:
                    inputs[name] = md_rec
                    realized_arguments[name] = md
                else:
                    inputs[name] = use.get_metadata_column(column_name, md_rec)
                    realized_arguments[name] = md.get_column(column_name)

            else:
                inputs[name] = realized_arguments[name] = argument

        for name, spec in self.parameter_specs.items():
            if name not in realized_arguments:
                realized_arguments[name] = spec.default

        use.action(
            use.UsageAction(plugin_id='mystery_stew', action_id=self.id),
            use.UsageInputs(**inputs),
            use.UsageOutputNames(**self.output_names),
        )

        for idx, (name, expected_type) in enumerate(self.expected_outputs):
            self._assert_output(use, name, expected_type, idx,
                                realized_arguments)

    @staticmethod
    def _fmt_regex(name, arg):
        line = argument_to_line(name, arg).strip()
        return re.escape(line)

    def _assert_output(self, use, output_name, expected_type, idx,
                       realized_arguments):
        output = use.get_result(output_name)
        output.assert_output_type(label='<generated>',
                                  semantic_type=expected_type)

        if idx == 0:
            for name, arg in realized_arguments.items():
                regex = self._fmt_regex(name, arg)
                output.assert_has_line_matching(label='<generated>',
                                                path='echo.txt',
                                                expression=regex)
        else:
            output.assert_has_line_matching(label='<generated>',
                                            path='echo.txt',
                                            expression=str(idx))