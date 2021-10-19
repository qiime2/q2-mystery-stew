# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import math
from typing import Union
from itertools import cycle, product


from qiime2.plugin import TypeMap, Int, Str, Bool, Choices

from q2_mystery_stew.type import (
    EchoOutputBranch1, EchoOutputBranch2, EchoOutputBranch3,
    SingleInt1, SingleInt2, WrappedInt1, WrappedInt2, IntWrapper)
from q2_mystery_stew.format import SingleIntFormat
from q2_mystery_stew.generators import FILTERS
from q2_mystery_stew.generators.base import (
    ParamSpec, ActionTemplate, Invocation)
from q2_mystery_stew.generators.primitive import (
    int_params, bool_params, float_params, string_params,
    primitive_union_params)
from q2_mystery_stew.generators.artifacts import (
    single_int1_1, single_int1_2, single_int2_1, single_int2_2, wrapped_int1_1,
    wrapped_int1_2, wrapped_int2_1, wrapped_int2_2)
from q2_mystery_stew.generators.collections import list_paramgen, set_paramgen

OUTPUT_STATES = [EchoOutputBranch1, EchoOutputBranch2, EchoOutputBranch3]


def generate_typemap_methods(filters):
    def should_add(filter_):
        assert filter_ in FILTERS
        # no filters are set, so add all, or add if filter is True
        return not filters or filters.get(filter_, False)

    mapped = []
    if should_add('strings') and should_add('ints'):
        mapped.append(typemap_str_int)
    if should_add('artifacts'):
        mapped.append(typemap_artifacts)
    if should_add('strings') and should_add('bools'):
        mapped.append(typemap_bool_flag)
    yield from map(_to_action, mapped)

    selected_types = []
    if should_add('ints'):
        selected_types.append(int_params)
    if should_add('bools'):
        selected_types.append(bool_params)
    if should_add('floats'):
        selected_types.append(float_params)
    if should_add('strings'):
        selected_types.append(string_params)
    if should_add('primitive_unions'):
        selected_types.append(primitive_union_params)

    yield from generate_the_matrix('typemap_the_matrix',
                                   [x() for x in selected_types])

    if should_add('collections'):
        yield from generate_the_matrix(
            'typemap_lists', [list_paramgen(x()) for x in selected_types])
        yield from generate_the_matrix(
            'typemap_sets', [set_paramgen(x()) for x in selected_types])


def _to_action(factory):
    spec, T_out, invokes = factory()
    parameter_specs = {spec.name: spec}
    registered_outputs = [('output', T_out)]
    invocation_domain = [Invocation(x, [('output', y)]) for x, y in invokes]
    return ActionTemplate(
        action_id=factory.__name__,
        parameter_specs=parameter_specs,
        registered_outputs=registered_outputs,
        invocation_domain=invocation_domain)


def typemap_str_int():
    T_in, T_out = TypeMap({
        Int: EchoOutputBranch1,
        Str: EchoOutputBranch2
    })

    param = ParamSpec('param', T_in, Union[int, str])
    invocations = [
        ({'param': 1}, EchoOutputBranch1),
        ({'param': 'foo'}, EchoOutputBranch2),
    ]

    return param, T_out, invocations


def typemap_bool_flag():
    T_in, T_out = TypeMap({
        Bool % Choices(True): EchoOutputBranch1,
        Bool % Choices(False): EchoOutputBranch2,
        Str % Choices('auto'): EchoOutputBranch3
    })

    param = ParamSpec('flag', T_in, Union[bool, str], default='auto')
    invocations = [
        ({'flag': True}, EchoOutputBranch1),
        ({'flag': False},  EchoOutputBranch2),
        ({'flag': 'auto'},  EchoOutputBranch3),
        ({}, EchoOutputBranch3)
    ]

    return param, T_out, invocations


def typemap_artifacts():
    T_in, T_out = TypeMap({
        SingleInt1: EchoOutputBranch1,
        SingleInt2: EchoOutputBranch2,
        IntWrapper[WrappedInt1 | WrappedInt2]: EchoOutputBranch3
    })

    param = ParamSpec('input', T_in, SingleIntFormat)
    invocations = [
        ({'input': single_int1_1}, EchoOutputBranch1),
        ({'input': single_int1_2}, EchoOutputBranch1),
        ({'input': single_int2_1}, EchoOutputBranch2),
        ({'input': single_int2_2}, EchoOutputBranch2),
        ({'input': wrapped_int1_1}, EchoOutputBranch3),
        ({'input': wrapped_int1_2}, EchoOutputBranch3),
        ({'input': wrapped_int2_1}, EchoOutputBranch3),
        ({'input': wrapped_int2_2}, EchoOutputBranch3),
    ]

    return param, T_out, invocations


def generate_the_matrix(action_base_id, selected_types):
    selected_lists = [list(generator) for generator in selected_types]
    longest = max(*map(len, selected_lists))
    # Set up a method that looks like this:
    # (param1,  param2,          paramN)  --> (output1,  output2)
    #  ------   ------           ------    |   -------   -------
    #  Int,     Int % Range,     ...       |   Out1,     Out1
    #  Str,     Str % Choices,   ...       |   Out1,     Out2
    #  Bool,    Bool % Choices,  ...       |   Out1,     Out3
    #  ...      ...              ...       |   Out2,     Out1
    #
    # branches of the typemap are obviously disjoint, and each param
    # represents a different refinement.
    # We test all of this with 1 invocation per row

    # treat output number as a radix expansion of EchoOutputBranch[1-3]'s
    num_outputs = math.ceil(math.log(len(selected_lists))
                            # change of base formula
                            / math.log(len(OUTPUT_STATES)))

    # each possible combination is a unique permutation of output states
    outputs = list(product(OUTPUT_STATES, repeat=num_outputs))

    # we are going to iterate column-wise, and then
    # transpose afterwards to create a dictionary for typemap

    # these are column-ordered
    qiime_types = []
    view_types = []
    base_names = []
    domains = []
    for col in zip(range(1, longest+1),
                   *[cycle(sel) for sel in selected_lists]):
        col_idx = col[0]
        types = []
        views = []
        branch_domain = []
        for template in col[1:]:
            types.append(template.qiime_type)
            views.append(template.view_type)
            branch_domain.append(template.domain[0])

        view_types.append(Union[tuple(views)])
        qiime_types.append(types)  # still a list, so creates list of lists
        base_names.append(f'param{col_idx}')
        domains.append(branch_domain)

    typevars = TypeMap({row: outputs[row_idx]
                        for row_idx, row in enumerate(zip(*qiime_types))})
    typevars = list(typevars)
    T_inputs = typevars[:longest]
    T_outputs = typevars[longest:]
    assert len(T_outputs) == num_outputs

    param_specs = {}
    param_specs_defaults = []
    for base_name, view, var, domain in zip(base_names, view_types, T_inputs,
                                            domains):
        param_specs[base_name] = ParamSpec(name=base_name,
                                           qiime_type=var,
                                           view_type=view)
        for i in range(len(selected_lists)):
            if i >= len(param_specs_defaults):
                param_specs_defaults.insert(i, {})
            param_specs_defaults[i][base_name] = ParamSpec(
                name=base_name, qiime_type=var, view_type=view,
                default=domain[i])

    registered_outputs = []
    for out_idx, var in enumerate(T_outputs, 1):
        registered_outputs.append((f'output{out_idx}', var))

    invocation_domain = []
    invocation_domain
    for row_idx, row in enumerate(zip(*domains)):
        inputs = {p: val for p, val in zip(base_names, row)}
        exp = [(name, out) for (name, _), out in zip(registered_outputs,
                                                     outputs[row_idx])]
        invocation_domain.append(Invocation(inputs, exp))

    yield ActionTemplate(
        action_id=action_base_id,
        parameter_specs=param_specs,
        registered_outputs=registered_outputs,
        invocation_domain=invocation_domain)

    for idx, param_specs in enumerate(param_specs_defaults):
        if action_base_id == 'typemap_the_matrix':
            if idx == 0:
                action_id = 'typemap_the_matrix_reloaded'
            elif idx == 1:
                action_id = 'typemap_the_matrix_revolutions'
            elif idx == 2:
                action_id = 'typemap_the_matrix_resurrections'
            else:
                action_id = f'typemap_the_matrix_{idx+2}'
        else:
            action_id = f'{action_base_id}_defaults{idx+1}'

        correct_invocation = invocation_domain[idx]
        invocation = Invocation({}, correct_invocation.expected_output_types)
        yield ActionTemplate(
                action_id=action_id,
                parameter_specs=param_specs,
                registered_outputs=registered_outputs,
                invocation_domain=[invocation])
