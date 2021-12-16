# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import re

import qiime2
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

    def __call__(self, use):
        inputs = {}
        realized_arguments = {}

        # This is needed to prevent namespace collision when reusing var inputs
        # when parameter domains end up being "rotated" around to test things
        # This dictionary should not survive beyond __call__
        memoized_vars = {}

        def do(use_method, *args):
            # name is always the first arg to a usage method
            name = args[0]
            if name not in memoized_vars:
                memoized_vars[name] = use_method(*args)
            return memoized_vars[name]

        for name, argument in self.arguments.items():
            spec = self.parameter_specs[name]

            if argument is None:
                inputs[name] = realized_arguments[name] = None

            elif is_semantic_type(spec.qiime_type):
                if type(argument) == list or type(argument) == set:
                    collection_type = type(argument)
                    realized_arguments[name] = collection_type()
                    inputs[name] = collection_type()

                    for arg in argument:
                        artifact = arg()
                        view = artifact.view(spec.view_type)
                        view.__hide_from_garbage_collector = artifact
                        var = do(use.init_artifact, arg.__name__, arg)

                        if collection_type == list:
                            realized_arguments[name].append(view)
                            inputs[name].append(var)
                        elif collection_type == set:
                            realized_arguments[name].add(view)
                            inputs[name].add(var)
                else:
                    artifact = argument()
                    view = artifact.view(spec.view_type)
                    view.__hide_from_garbage_collector = artifact
                    var = do(use.init_artifact, argument.__name__, argument)

                    realized_arguments[name] = view
                    inputs[name] = var

            elif is_metadata_type(spec.qiime_type):
                if is_metadata_column_type(spec.qiime_type):
                    factory, column_name = argument
                else:
                    factory, column_name = argument, None

                if type(factory) is list:
                    realized_factories = [f() for f in factory]
                    factories = factory
                else:
                    realized_factories = [factory()]
                    factories = [factory]

                md_vars = []
                realized_mds = []
                for md, factory in zip(realized_factories, factories):
                    if not isinstance(md, qiime2.Metadata):
                        var = do(use.init_artifact, factory.__name__, factory)
                        md_var = do(use.view_as_metadata,
                                    factory.__name__ + "_md", var)
                        md = md.view(qiime2.Metadata)
                    else:
                        md_var = do(use.init_metadata,
                                    factory.__name__, factory)

                    md_vars.append(md_var)
                    realized_mds.append(md)

                if len(md_vars) > 1:
                    md_var = do(use.merge_metadata,
                                '_'.join([f.__name__ for f in factories]),
                                *md_vars)
                    md = realized_mds[0].merge(*realized_mds[1:])
                else:
                    md_var = md_vars[0]
                    md = realized_mds[0]

                if column_name is None:
                    realized_arguments[name] = md
                    inputs[name] = md_var
                else:
                    col_var = do(use.get_metadata_column,
                                 '%s_%s' % (md_var.name, column_name),
                                 column_name,
                                 md_var)
                    realized_arguments[name] = md.get_column(column_name)
                    inputs[name] = col_var

            else:
                inputs[name] = realized_arguments[name] = argument

        for name, spec in self.parameter_specs.items():
            if name not in realized_arguments:
                realized_arguments[name] = spec.default

        # no need to memoize, these outputs will not be used (only assertions)
        computed_results = use.action(
            use.UsageAction(plugin_id='mystery_stew', action_id=self.id),
            use.UsageInputs(**inputs),
            use.UsageOutputNames(**self.output_names),
        )

        for idx, (name, expected_type) in enumerate(self.expected_outputs):
            self._assert_output(computed_results, name, expected_type, idx,
                                realized_arguments)

    @staticmethod
    def _fmt_regex(name, arg):
        line = argument_to_line(name, arg).strip()
        return re.escape(line)

    def _assert_output(self, computed_results, output_name, expected_type, idx,
                       realized_arguments):
        output = computed_results[idx]
        output.assert_output_type(semantic_type=expected_type)

        if idx == 0:
            for name, arg in realized_arguments.items():
                regex = self._fmt_regex(name, arg)
                output.assert_has_line_matching(path='echo.txt',
                                                expression=regex)
        else:
            output.assert_has_line_matching(path='echo.txt',
                                            expression=str(idx + 1))
