# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from qiime2.sdk import PluginManager, usage

from q2_mystery_stew.plugin_setup import create_plugin


class TestTemplates(unittest.TestCase):
    package = 'q2_mystery_stew.test'
    plugin = create_plugin(ints=True)

    def setUp(self):
        pm = PluginManager(add_plugins=False)
        pm.add_plugin(self.plugin)

    def test_examples(self):
        self.execute_examples()

    def execute_examples(self):
        if self.plugin is None:
            raise ValueError('Attempted to run `execute_examples` without '
                             'configuring test harness.')
        i = 0
        for _, action in self.plugin.actions.items():
            for name, example_f in action.examples.items():
                with self.subTest(example=name, i=i):
                    use = usage.ExecutionUsage()
                    example_f(use)
                    i += 1
