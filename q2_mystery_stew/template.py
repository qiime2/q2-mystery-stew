# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import json
from inspect import Signature, Parameter

import qiime2

from q2_mystery_stew.templatable_echo_fmt import EchoOutputFmt
from q2_mystery_stew.format import SingleIntFormat


# TODO: will this be dead code?
def rewrite_function_signature(function, inputs, params, num_outputs, name):
    output = tuple([EchoOutputFmt] * num_outputs)

    input_params = [Parameter(name, Parameter.POSITIONAL_ONLY,
                              annotation=type_)
                    for name, type_ in inputs.items()]

    input_params.extend([Parameter(name, Parameter.POSITIONAL_ONLY,
                                   annotation=type_)
                        for name, type_ in params.items()])

    annotations = {}
    annotations.update(inputs)
    annotations.update(params)
    annotations.update({'return': output})

    function.__signature__ = \
        Signature(input_params, return_annotation=output)
    function.__annotations__ = annotations
    function.__name__ = name


def disguise_function(function, name, parameters, num_outputs):
    if num_outputs == 1:
        outputs = EchoOutputFmt
    else:
        outputs = tuple([EchoOutputFmt] * num_outputs)

    annotations = {p.name: p.annotation for p in parameters}
    annotations['return'] = outputs

    function.__signature__ = Signature(parameters, return_annotation=outputs)
    function.__annotations__ = annotations
    function.__name__ = name


# TODO: If we see a set of semantic types, we want to make sure we output it as a list
# If we have a list sort on repr of items
def argument_to_line(name, arg):
    value = arg
    expected_type = type(arg).__name__

    if isinstance(arg, SingleIntFormat):
        value = arg.get_int()
    elif isinstance(arg, qiime2.Metadata):
        value = arg.to_dataframe().to_json()
    elif isinstance(arg, (qiime2.CategoricalMetadataColumn,
                          qiime2.NumericMetadataColumn)):
        value = arg.to_series().to_json()

    if type(arg) is list or type(arg) is set:
        temp = []
        for i in value:
            if isinstance(i, SingleIntFormat):
                temp.append(i.get_int())
                expected_type = 'list'
            else:
                temp.append(i)
        value = sorted(temp, key=repr)

    return json.dumps([name, value, expected_type]) + '\n'


def write_output(**kwargs):
    output = EchoOutputFmt()
    with output.open() as fh:
        for name, arg in kwargs.items():
            fh.write(argument_to_line(name, arg))

    return output


def function_template_1output(**kwargs):
    output = write_output(**kwargs)

    return output


def function_template_2output(**kwargs):
    output = write_output(**kwargs)
    output2 = EchoOutputFmt()

    with output2.open() as fh:
        fh.write('2')

    return output, output2


def function_template_3output(**kwargs):
    output = write_output(**kwargs)
    output2 = EchoOutputFmt()
    output3 = EchoOutputFmt()

    with output2.open() as fh:
        fh.write('2')

    with output3.open() as fh:
        fh.write('3')

    return output, output2, output3
