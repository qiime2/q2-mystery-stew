# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin.testing import TestPluginBase


class TestTemplates(TestPluginBase):
    package = 'q2_mystery_stew.test'

    def test_examples(self):
        self.execute_examples()
