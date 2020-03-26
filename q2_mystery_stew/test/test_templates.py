# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import unittest

from qiime2.sdk import usage

from q2_mystery_stew.plugin_setup import plugin


class TestTemplates(unittest.TestCase):
    def test_int_cases(self):
        use = usage.DiagnosticUsage()

        for action_ in plugin.actions.values():
            for example in action_.examples.values():
                example(use)
