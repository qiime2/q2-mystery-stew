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

from qiime2.plugin import Int, Range

from q2_mystery_stew.plugin_setup import plugin
from q2_mystery_stew.templatable_echo_fmt import EchoOutputFmt

Param = namedtuple('Param', ['name', 'type', 'domain'])


class TestTemplates(unittest.TestCase):
    def test_int_cases(self):
        int_args = {
            'single_int': Param('single_int', Int, (-4, 0, 4)),
            'int_range_one_arg': Param('int_range_one_arg',
                                       Int % Range(5), (-4, 0, 4)),
            'int_range_two_args': Param('int_range_two_args',
                                        Int % Range(-5, 5), (-4, 0, 4))
        }

        for method in plugin.methods.values():
            raise ValueError(method)
            signature = method.signature
            args = []

            for param in signature.parameters:
                param_type = param.split('__')[0]
                args.append(int_args[param_type].domain)

            for arg_list in product(*args):
                output = method(*arg_list)

                with output[0].view(EchoOutputFmt).open() as fh:
                    lines = ''.join(line for line in fh)

                    for arg, param_name in zip(arg_list, signature.parameters):
                        self.assertIn(f'{param_name}: {arg}', lines)

                if len(output) > 1:
                    with output[1].view(EchoOutputFmt).open() as fh:
                        lines = ''.join(line for line in fh)
                        self.assertIn('second', lines)

                if len(output) > 2:
                    with output[2].view(EchoOutputFmt).open() as fh:
                        lines = ''.join(line for line in fh)
                        self.assertIn('third', lines)
