# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from .primitive import (int_params, float_params, string_params, bool_params,
                        primitive_union_params)
from .metadata import metadata_params
from .artifacts import artifact_params
from .collections import list_paramgen, set_paramgen
from .base import ParamTemplate


BASIC_GENERATORS = {
    'ints': int_params,
    'floats': float_params,
    'strings': string_params,
    'bools': bool_params,
    'metadata': metadata_params,
    'primitive_unions': primitive_union_params,
    'artifacts': artifact_params
}
FILTERS = {*BASIC_GENERATORS.keys(), 'collections', 'typemaps'}


def get_param_generators(**filters):
    selected_generators = []

    def should_add(filter_):
        # no filters are set, so add all, or add if filter is True
        return not filters or filters.get(filter_, False)

    add_collections = should_add('collections')

    for key, generator in BASIC_GENERATORS.items():
        if key not in FILTERS:
            raise ValueError("Filter %r is not recognized by mystery-stew"
                             % key)
        if should_add(key):
            selected_generators.append(generator())
            if add_collections and key != 'metadata':
                selected_generators.append(list_paramgen(generator()))
                selected_generators.append(set_paramgen(generator()))

    if not selected_generators:
        raise ValueError("At least one filter must be set to True")

    return selected_generators


__all__ = ['int_params', 'float_params', 'string_params', 'bool_params',
           'primitive_union_params', 'metadata_params', 'artifact_params',
           'list_paramgen', 'set_paramgen', 'BASIC_GENERATORS', 'FILTERS',
           'get_param_generators', 'ParamTemplate']
