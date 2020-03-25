# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin import Plugin
from itertools import product
from collections import namedtuple

from qiime2.plugin import Int, Range

import q2_mystery_stew
from q2_mystery_stew.template import rewrite_function_signature, \
                                     function_template_1output, \
                                     function_template_2output, \
                                     function_template_3output
from q2_mystery_stew.templatable_echo_fmt import EchoOutput, EchoOutputFmt, \
                                                 EchoOutputDirFmt

plugin = Plugin(
    name='mystery-stew',
    version=q2_mystery_stew.__version__,
    website='https://github.com/qiime2/q2-mystery-stew',
    package='q2_mystery_stew',
    description=('This QIIME 2 plugin Templates out arbitrary QIIME 2 actions '
                 'to test interfaces. '),
    short_description='Plugin for generating arbitrary QIIME 2 actions.'
)

Sig = namedtuple('Sig', ['num_inputs', 'num_outputs', 'signature'])
Param = namedtuple('Param', ['name', 'type', 'domain'])

function_signatures = (function_template_1output,
                       function_template_2output,
                       function_template_3output)


def generate_signatures(args):
    for num_inputs in range(1, len(args) + 1):
        for num_outputs in range(1, len(function_signatures) + 1):
            yield Sig(num_inputs, num_outputs,
                      function_signatures[num_outputs - 1])


int_args = {
    'single_int': Param('single_int', Int, (-4, 0, 4)),
    'int_range_one_arg': Param('int_range_one_arg',
                               Int % Range(5), (-4, 0, 4)),
    'int_range_two_args': Param('int_range_two_args',
                                Int % Range(-5, 5), (-4, 0, 4))
}

num_functions = 0
signatures = generate_signatures(int_args)

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
                                   f'func_{num_functions}')

        output = []
        for i in range(signature.num_outputs):
            output.append((str(i), EchoOutput))

        plugin.methods.register_function(
            function=signature.signature,
            inputs={},
            parameters=param_dict,
            outputs=output,
            name=f'func_{num_functions}',
            description=''
        )
        num_functions += 1

plugin.register_formats(EchoOutputFmt, EchoOutputDirFmt)
plugin.register_semantic_types(EchoOutput)
plugin.register_semantic_type_to_format(EchoOutput, EchoOutputDirFmt)
