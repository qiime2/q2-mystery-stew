# ----------------------------------------------------------------------------
# Copyright (c) 2020-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from collections import deque

from qiime2.core.type import Collection
from qiime2.sdk.util import is_metadata_type, is_semantic_type

from q2_mystery_stew.type import EchoOutput
from q2_mystery_stew.generators.base import ActionTemplate, Invocation


def generate_single_type_methods(generator):
    for idx, param in enumerate(generator, 1):
        action_id = f'{generator.__name__}_{idx}'
        qiime_outputs = [('only_output', EchoOutput)]
        specs = {}
        defaults = {}

        primary = param.mint_spec()
        specs[primary.name] = primary

        optional = param.mint_spec(prefix='optional_', default=None)
        specs[optional.name] = optional
        defaults[optional.name] = optional.default

        if (not is_metadata_type(param.qiime_type)
                and not is_semantic_type(param.qiime_type)):
            for domain_idx, arg in enumerate(param.domain):
                default = param.mint_spec(f'default{domain_idx}_', default=arg)
                specs[default.name] = default
                defaults[default.name] = default.default

        # USAGE: pass each value in the domain for required args
        domain = [Invocation({primary.name: arg}, qiime_outputs)
                  for arg in param.domain]

        # USAGE: pass all defaults manually
        arg = param.domain[-1]
        domain.append(Invocation({primary.name: arg, **defaults},
                                 qiime_outputs))

        # USAGE: pass a different value to all defaults
        if len(param.domain) > 1:
            # if len(domain) is 1, then there would be nothing to rotate and
            # the arguments would be the same as the default
            shifted = deque([arg, arg, *param.domain])
            shifted.rotate(1)
            domain.append(Invocation({k: v for k, v in zip(specs, shifted)},
                                     qiime_outputs))

        yield ActionTemplate(action_id=action_id,
                             parameter_specs=specs,
                             registered_outputs=qiime_outputs,
                             invocation_domain=domain)


# TODO: Add functions to do with generating output collection methods here
def generate_multiple_output_methods():
    for num_outputs in range(1, 5+1):
        action_id = f'multiple_outputs_{num_outputs}'

        qiime_outputs = []
        for idx in range(1, num_outputs+1):
            qiime_outputs.append((f'output{idx}', EchoOutput))

        yield ActionTemplate(action_id=action_id,
                             parameter_specs={},
                             registered_outputs=qiime_outputs,
                             invocation_domain=[Invocation({}, qiime_outputs)])


def generate_output_collection_methods():
    action_id = 'collection_only'
    qiime_outputs = [('output', Collection[EchoOutput])]
    yield ActionTemplate(action_id=action_id,
                         parameter_specs={},
                         registered_outputs=qiime_outputs,
                         invocation_domain=[Invocation({}, qiime_outputs)])

    action_id = 'collection_first'
    qiime_outputs = [('output_collection', Collection[EchoOutput]),
                     ('output', EchoOutput)]
    yield ActionTemplate(action_id=action_id,
                         parameter_specs={},
                         registered_outputs=qiime_outputs,
                         invocation_domain=[Invocation({}, qiime_outputs)])

    action_id = 'collection_second'
    qiime_outputs = [('output', EchoOutput),
                     ('output_collection', Collection[EchoOutput])]
    yield ActionTemplate(action_id=action_id,
                         parameter_specs={},
                         registered_outputs=qiime_outputs,
                         invocation_domain=[Invocation({}, qiime_outputs)])
