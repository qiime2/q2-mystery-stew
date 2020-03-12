# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import unittest

from qiime2.plugin import Int, Range, List, Str

from q2_mystery_stew.template import TemplatableCallable
from q2_mystery_stew.plugin_setup import plugin
from q2_mystery_stew.templatable_echo_fmt import outputFile, outputFileFmt


class TestTemplates(unittest.TestCase):
    def setUp(self):
        self.int_args = {
            'single_int': Int,
            'int_range_no_args': Int % Range(),
            'int_range_one_arg': Int % Range(10),
            'int_range_two_args': Int % Range(5, 10),
            'int_list': List[Int]
        }

    def test_int_cases(self):
        example = \
            TemplatableCallable({},
                                self.int_args,
                                (outputFileFmt,), 'foo')

        plugin.methods.register_function(
            function=example.__call__.__func__,
            inputs={},
            parameters=self.int_args,
            outputs=[('file', outputFile)],
            name='test', description='test')

        example1 = \
            TemplatableCallable({},
                                {'string': Str},
                                (outputFileFmt,), 'bar')

        plugin.methods.register_function(
            function=example1.__call__.__func__,
            inputs={},
            parameters={'string': Str},
            outputs=[('file', outputFile)],
            name='test', description='test')

        plugin.actions['foo'](1, 2, 3, 6, [1, 2])
        plugin.actions['foo'].asynchronous(1, 2, 3, 6, [1, 2])
        plugin.actions['bar']('abawda')
        plugin.actions['bar'].asynchronous('adawdadwa')

    def test_z(self):
        pass
