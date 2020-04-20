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


def write_output(output, **kwargs):
    with output.open() as fh:
        for name, arg in kwargs.items():
            if 'md' in name:
                arg = arg.to_dataframe()
                arg = str(arg)
                arg = arg.replace('[', ':').replace(']', ':')
            elif type(arg) == list or type(arg) == set:
                arg_str = ''
                for val in arg:
                    arg_str += f': {val}'

                arg = arg_str

            fh.write(f'{name}: {arg}\n')

    return output


def function_template_1output(**kwargs):
    output = write_output(EchoOutputFmt(), **kwargs)

    return output,


def function_template_2output(**kwargs):
    output = write_output(EchoOutputFmt(), **kwargs)
    output2 = EchoOutputFmt()

    with output2.open() as fh:
        fh.write('second')

    return output, output2


def function_template_3output(**kwargs):
    output = write_output(EchoOutputFmt(), **kwargs)
    output2 = EchoOutputFmt()
    output3 = EchoOutputFmt()

    with output2.open() as fh:
        fh.write('second')

    with output3.open() as fh:
        fh.write('third')

    return output, output2, output3
