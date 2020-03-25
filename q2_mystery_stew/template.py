# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from inspect import Signature, Parameter

from q2_mystery_stew.templatable_echo_fmt import outputFileFmt


def rewrite_function_signature(function, inputs, params, num_outputs, name):
    output = []
    for i in range(num_outputs):
        output.append(outputFileFmt)
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
    output = outputFileFmt()

    with output.open() as fh:
        for kw, arg in kwargs.items():
            fh.write(f'\n{kw}: {arg}')

    return output,


def function_template_2output(**kwargs):
    output = outputFileFmt()
    output2 = outputFileFmt()

    with output.open() as fh:
        for kw, arg in kwargs.items():
            fh.write(f'\n{kw}: {arg}')

    with output2.open() as fh:
        fh.write('second')

    return output, output2


def function_template_3output(**kwargs):
    output = outputFileFmt()
    output2 = outputFileFmt()
    output3 = outputFileFmt()

    with output.open() as fh:
        for kw, arg in kwargs.items():
            fh.write(f'\n{kw}: {arg}')

    with output2.open() as fh:
        fh.write('second')

    with output3.open() as fh:
        fh.write('third')

    return output, output2, output3
