# ----------------------------------------------------------------------------
# Copyright (c) 2020-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json
from inspect import Signature

import qiime2

from q2_mystery_stew.format import SingleIntFormat, EchoOutputFmt


def get_disguised_echo_function(id, python_parameters, num_outputs):
    TEMPLATES = [
        _function_template_1output,
        _function_template_2output,
        _function_template_3output,
        _function_template_4output,
        _function_template_5output,
    ]

    function = TEMPLATES[num_outputs - 1]
    disguise_echo_function(function, id, python_parameters, num_outputs)

    return function


def disguise_echo_function(function, name, parameters, num_outputs):
    if num_outputs == 1:
        outputs = EchoOutputFmt
    else:
        outputs = tuple([EchoOutputFmt] * num_outputs)

    annotations = {p.name: p.annotation for p in parameters}
    annotations['return'] = outputs

    function.__signature__ = Signature(parameters, return_annotation=outputs)
    function.__annotations__ = annotations
    function.__name__ = name


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

    # We need a list so we can jsonize it (cannot jsonize sets)
    sort = False
    if type(arg) is list or type(arg) is set:
        temp = []
        for i in value:
            # If we are given a set of artifacts it will be turned into a list
            # by the framework, so we need to be ready to accept a list
            if isinstance(i, SingleIntFormat):
                temp.append(i.get_int())
                expected_type = 'list'
                sort = True
            else:
                temp.append(i)
        # If we turned a set into a list for json purposes, we need to sort it
        # to ensure it is always in the same order
        if type(arg) is set or sort:
            value = sorted(temp, key=repr)
        else:
            value = temp

    return json.dumps([name, value, expected_type]) + '\n'


def _echo_outputs(kwargs, num_outputs):
    output = EchoOutputFmt()
    with output.open() as fh:
        for name, arg in kwargs.items():
            fh.write(argument_to_line(name, arg))

    if num_outputs > 1:
        output = (output, *map(lambda x: EchoOutputFmt(),
                               range(1, num_outputs)))
        for idx, fmt in enumerate(output[1:], 2):
            with fmt.open() as fh:
                fh.write(str(idx))

    return output


def _function_template_1output(**kwargs):
    return _echo_outputs(kwargs, 1)


def _function_template_2output(**kwargs):
    return _echo_outputs(kwargs, 2)


def _function_template_3output(**kwargs):
    return _echo_outputs(kwargs, 3)


def _function_template_4output(**kwargs):
    return _echo_outputs(kwargs, 4)


def _function_template_5output(**kwargs):
    return _echo_outputs(kwargs, 5)
