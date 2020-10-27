# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin.testing import TestPluginBase

from q2_mystery_stew.plugin_setup import create_plugin

class TestTemplates(TestPluginBase):
    package = 'q2_mystery_stew.test'
    plugin = create_plugin()

    def test_examples(self):
        self.execute_examples()
