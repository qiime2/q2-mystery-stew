# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pytest

from qiime2.sdk import PluginManager, usage

from q2_mystery_stew.plugin_setup import create_plugin


def get_tests():
    plugin = create_plugin()
    tests = []
    pm = PluginManager(add_plugins=False)
    pm.add_plugin(plugin)
    for action in plugin.actions.values():
        for name in action.examples:
            tests.append((action, name))
    return tests


def _labeler(val):
    if hasattr(val, 'id'):
        return val.id
    return val


@pytest.mark.parametrize('action,example', get_tests(), ids=_labeler)
def test_case(action, example):
    example_f = action.examples[example]
    use = usage.ExecutionUsage()
    use_async = usage.ExecutionUsage(asynchronous=True)
    example_f(use)
    example_f(use_async)
