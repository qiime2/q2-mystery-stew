# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import unittest
from itertools import product
from collections import namedtuple

from qiime2.plugin import Int, Str, Range

from q2_mystery_stew.template import rewrite_function_signature, \
                                     function_template_1output, \
                                     function_template_2output, \
                                     function_template_3output
from q2_mystery_stew.plugin_setup import plugin
from q2_mystery_stew.templatable_echo_fmt import outputFile, outputFileFmt


Signature = namedtuple('Signature', ['num_inputs', 'num_outputs', 'signature'])
Parameter = namedtuple('Parameter', ['name', 'type', 'domain'])


# We need to generate all combinations of template, args, and inputs
# We want to create named tuples of these things and yield them,
# itertools.product allows for easy cartesian product creation
class TestTemplates(unittest.TestCase):
    int_args = {
        'single_int': Int,
        'int_range_one_arg': Int % Range(5),
        'int_range_two_args': Int % Range(-5, 5)
    }

    function_signatures = (function_template_1output,
                           function_template_2output,
                           function_template_3output)

    # int_args = (
    #     Parameter('single_int', Int, (-4, 0, 4)),
    #     Parameter('int_range_one_arg', Int % Range(5), (-4, 0, 4)),
    #     Parameter('int_range_two_args', Int % Range(-5, 5), (-4, 0, 4))
    # )

    def generate_signatures(self):
        for num_inputs in range(1, 4):
            for num_outputs in range(1, 4):
                yield Signature(num_inputs, num_outputs,
                                self.function_signatures[num_outputs - 1])

    def test_int_cases(self):
        num_functions = 0

        signatures = self.generate_signatures()
        for signature in signatures:
            for params in product(self.int_args, repeat=signature.num_inputs):
                rewrite_function_signature(signature.signature,
                                           None,
                                           params,
                                           signature.num_outputs,
                                           str(num_functions))

                print(num_functions)
                plugin.methods.register_function(
                    function=signature.signature,
                    inputs={},
                    parameters=params,
                    outputs={},
                    name=str(num_functions),
                    description=str(num_functions)
                )
                num_functions += 1

        raise ValueError(num_functions)

        rewrite_function_signature({},
                                   self.int_args,
                                   (outputFileFmt,), 'foo')

        plugin.methods.register_function(
            function=function_template_1output,
            inputs={},
            parameters=self.int_args,
            outputs=[('file', outputFile)],
            name='test', description='test')

        rewrite_function_signature({},
                                   {'string': Str},
                                   (outputFileFmt,), 'bar')

        plugin.methods.register_function(
            function=function_template_1output,
            inputs={},
            parameters={'string': Str},
            outputs=[('file', outputFile)],
            name='test', description='test')

        x = plugin.actions['foo'](-4, -4, 4, 4, [1, 2])
        plugin.actions['foo'].asynchronous(-4, -4, 4, 4, [1, 2])

        plugin.actions['bar']('abawda')
        plugin.actions['bar'].asynchronous('adawdadwa')

        with x.file.view(outputFileFmt).open() as fh:
            lines = ''.join(line for line in fh)

        raise ValueError(lines)
        self.assertIn('single_int: -4', lines)

    def test_z(self):
        rewrite_function_signature({},
                                   {'string': Str},
                                   (outputFileFmt,), 'bar')

        plugin.methods.register_function(
            function=function_template_1output,
            inputs={},
            parameters={'string': Str},
            outputs=[('file', outputFile)],
            name='test', description='test')

        plugin.actions['foo'](1, 2, 3, 4, [1, 2])
        plugin.actions['foo'].asynchronous(1, 2, 3, 4, [1, 2])

        plugin.actions['bar']('abawda')
        plugin.actions['bar'].asynchronous('adawdadwa')
