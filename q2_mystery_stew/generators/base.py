# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from inspect import Parameter
from collections import namedtuple


class ParamSpec:
    NoDefault = Parameter.empty

    def __init__(self, name, qiime_type, view_type, default):
        self.name = name
        self.qiime_type = qiime_type
        self.view_type = view_type
        self.default = default


class ParamTemplate:
    def __init__(self, base_name, qiime_type, view_type, domain):
        self.base_name = base_name
        self.qiime_type = qiime_type
        self.view_type = view_type
        self.domain = domain

    def mint_spec(self, prefix='', default=ParamSpec.NoDefault):
        return ParamSpec(prefix+self.base_name,
                         self.qiime_type,
                         self.view_type,
                         default)


Invocation = namedtuple('Invocation', ['kwargs', 'expected_output_types'])
ActionTemplate = namedtuple('ActionTemplate', ['action_id',
                                               'parameter_specs',
                                               'registered_outputs',
                                               'invocation_domain'])
