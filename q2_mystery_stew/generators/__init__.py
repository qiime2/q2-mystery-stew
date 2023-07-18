# ----------------------------------------------------------------------------
# Copyright (c) 2020-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from .primitive import (int_params, float_params, string_params, bool_params,
                        primitive_union_params)
from .metadata import metadata_params
from .artifacts import artifact_params
from .collections import list_paramgen, collection_paramgen
from .actions import (generate_single_type_methods,
                      generate_multiple_output_methods,
                      generate_output_collection_methods)
from .base import ParamTemplate, ActionTemplate, ParamSpec, Invocation

BASIC_GENERATORS = {
    'artifacts': artifact_params,
    'metadata': metadata_params,
    'ints': int_params,
    'bools': bool_params,
    'floats': float_params,
    'strings': string_params,
    'primitive_unions': primitive_union_params,
}
FILTERS = {*BASIC_GENERATORS.keys(), 'collections', 'typemaps', 'outputs'}

from .typemaps import generate_typemap_methods  # noqa: E402


def get_param_generators(**filters):
    selected_generators = []

    def should_add(filter_):
        # no filters are set, so add all, or add if filter is True
        return not filters or filters.get(filter_, False)

    add_collections = should_add('collections')
    lists = []
    collections = []
    for key, generator in BASIC_GENERATORS.items():
        if should_add(key):
            selected_generators.append(generator())
            if add_collections and key != 'metadata':
                lists.append(list_paramgen(generator()))
                collections.append(collection_paramgen(generator()))

    selected_generators.extend(lists)
    selected_generators.extend(collections)

    return selected_generators


__all__ = ['int_params', 'float_params', 'string_params', 'bool_params',
           'primitive_union_params', 'metadata_params', 'artifact_params',
           'list_paramgen', 'collection_paramgen',
           'generate_single_type_methods', 'generate_multiple_output_methods',
           'generate_output_collection_methods', 'generate_typemap_methods',
           'BASIC_GENERATORS', 'FILTERS', 'get_param_generators',
           'ParamTemplate', 'ParamSpec', 'ActionTemplate', 'Invocation']
