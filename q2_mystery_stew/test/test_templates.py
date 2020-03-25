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

from q2_mystery_stew.template import rewrite_function_signature, \
                                     function_template_1output, \
                                     function_template_2output, \
                                     function_template_3output
from q2_mystery_stew.plugin_setup import plugin
from q2_mystery_stew.templatable_echo_fmt import outputFile, outputFileFmt


Sig = namedtuple('Sig', ['num_inputs', 'num_outputs', 'signature'])
Param = namedtuple('Param', ['name', 'type', 'domain'])


class TestTemplates(unittest.TestCase):
    function_signatures = (function_template_1output,
                           function_template_2output,
                           function_template_3output)

    def generate_signatures(self, args):
        for num_inputs in range(1, len(args) + 1):
            for num_outputs in range(1, len(self.function_signatures) + 1):
                yield Sig(num_inputs, num_outputs,
                          self.function_signatures[num_outputs - 1])

    def test_int_cases(self):
        int_args = {
            'single_int': Param('single_int', Int, (-4, 0, 4)),
            'int_range_one_arg': Param('int_range_one_arg',
                                       Int % Range(5), (-4, 0, 4)),
            'int_range_two_args': Param('int_range_two_args',
                                        Int % Range(-5, 5), (-4, 0, 4))
        }

        num_functions = 0
        signatures = self.generate_signatures(int_args)

        for signature in signatures:
            for params in product(int_args.values(),
                                  repeat=signature.num_inputs):
                param_dict = {}
                for i, param in enumerate(params):
                    param_dict.update({param.name + f'__{i}': param.type})

                rewrite_function_signature(signature.signature,
                                           {},
                                           param_dict,
                                           signature.num_outputs,
                                           f'_{num_functions}')

                output = []
                for i in range(signature.num_outputs):
                    output.append((str(i), outputFile))

                plugin.methods.register_function(
                    function=signature.signature,
                    inputs={},
                    parameters=param_dict,
                    outputs=output,
                    name=f'_{num_functions}',
                    description=str(num_functions)
                )
                num_functions += 1

        for method in plugin.methods.values():
            signature = method.signature
            args = []

            for param in signature.parameters:
                param_type = param.split('__')[0]
                args.append(int_args[param_type].domain)

            for arg_list in product(*args):
                output = method(*arg_list)

                with output[0].view(outputFileFmt).open() as fh:
                    lines = ''.join(line for line in fh)

                    for arg, param_name in zip(arg_list, signature.parameters):
                        self.assertIn(f'{param_name}: {arg}', lines)

                if len(output) > 1:
                    with output[1].view(outputFileFmt).open() as fh:
                        lines = ''.join(line for line in fh)
                        self.assertIn('second', lines)

                if len(output) > 2:
                    with output[2].view(outputFileFmt).open() as fh:
                        lines = ''.join(line for line in fh)
                        self.assertIn('third', lines)
