# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import inspect

from q2_mystery_stew.templatable_echo_fmt import outputFileFmt


def rewrite_function_signature(function, inputs, params, output, name):
    pass
    #raise ValueError(params)
    # input_params = [inspect.Parameter(name,
    #                 inspect.Parameter.POSITIONAL_ONLY,
    #                 annotation=type_)
    #                 for name, type_ in input_.items()]
    # input_params.extend([inspect.Parameter(name,
    #                      inspect.Parameter.POSITIONAL_ONLY,
    #                      annotation=type_)
    #                      for name, type_ in params.items()])

    # annotations = input_
    # annotations.update(params)
    # annotations.update({'return': output})

    # function_template.__signature__ = \
    #     inspect.Signature(input_params, return_annotation=output)
    # function_template.__annotations__ = annotations
    # function_template.__name__ = name


def function_template_1output(**kwargs):
    output = outputFileFmt()

    with output.open() as fh:
        for kw, arg in kwargs.items():
            fh.write(f'\n{kw}: {arg}')

    return output


def function_template_2output(**kwargs):
    output = outputFileFmt()
    output = outputFileFmt()  # some output file that says it's the second one

    with output.open() as fh:
        for kw, arg in kwargs.items():
            fh.write(f'\n{kw}: {arg}')

    return output, output


def function_template_3output(**kwargs):
    output = outputFileFmt()
    output = outputFileFmt()  # some output file that says it's the second one
    output = outputFileFmt()  # some output file that says it's the third one

    with output.open() as fh:
        for kw, arg in kwargs.items():
            fh.write(f'\n{kw}: {arg}')

    return output, output, output
