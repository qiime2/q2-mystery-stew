# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from inspect import Signature, Parameter

from q2_mystery_stew.templatable_echo_fmt import EchoOutputFmt


def rewrite_function_signature(function, inputs, params, num_outputs, name):
    output = []
    for i in range(num_outputs):
        output.append(EchoOutputFmt)
    output = tuple(output)

    input_params = [Parameter(name, Parameter.POSITIONAL_ONLY,
                              annotation=type_)
                    for name, type_ in inputs.items()]

    input_params.extend([Parameter(name, Parameter.POSITIONAL_ONLY,
                                   annotation=type_)
                        for name, type_ in params.items()])

    annotations = inputs
    annotations.update(params)
    annotations.update({'return': output})

    function.__signature__ = \
        Signature(input_params, return_annotation=output)
    function.__annotations__ = annotations
    function.__name__ = name


def function_template_1output(**kwargs):
    output = EchoOutputFmt()

    # TODO: Remove
    # with open('/home/anthony/tst/test.txt', 'a') as fh:
    #     for kw, arg in kwargs.items():
    #         fh.write(f'{kw}: {arg}\n')
    #     fh.write('\n')
    with output.open() as fh:
        for kw, arg in kwargs.items():
            fh.write(f'{kw}: {arg}\n')

    return output,


def function_template_2output(**kwargs):
    output = EchoOutputFmt()
    output2 = EchoOutputFmt()

    # TODO: Remove
    # with open('/home/anthony/tst/test.txt', 'a') as fh:
    #     for kw, arg in kwargs.items():
    #         fh.write(f'{kw}: {arg}\n')
    #     fh.write('\n')
    with output.open() as fh:
        for kw, arg in kwargs.items():
            fh.write(f'{kw}: {arg}\n')

    with output2.open() as fh:
        fh.write('second')

    return output, output2


def function_template_3output(**kwargs):
    output = EchoOutputFmt()
    output2 = EchoOutputFmt()
    output3 = EchoOutputFmt()

    # TODO: Remove
    # with open('/home/anthony/tst/test.txt', 'a') as fh:
    #     for kw, arg in kwargs.items():
    #         fh.write(f'{kw}: {arg}\n')
    #     fh.write('\n')
    with output.open() as fh:
        for kw, arg in kwargs.items():
            fh.write(f'{kw}: {arg}\n')

    with output2.open() as fh:
        fh.write('second')

    with output3.open() as fh:
        fh.write('third')

    return output, output2, output3
