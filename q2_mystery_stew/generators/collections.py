# ----------------------------------------------------------------------------
# Copyright (c) 2020-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import itertools

from qiime2.plugin import List, Collection
from qiime2.core.type.util import is_semantic_type

from q2_mystery_stew.generators.base import ParamTemplate


def underpowered_set(iterable):
    """k of 1-tuple, 2 of 2-tuple, and a single k-tuple"""
    tuplek = tuple(iterable)
    pairs2 = itertools.combinations(tuplek, 2)

    for tuple1 in tuplek:
        yield (tuple1,)
    for tuple2, _ in zip(pairs2, range(2)):
        yield tuple2

    yield tuplek


def list_paramgen(generator):
    def make_list():
        for param in generator:
            if is_semantic_type(param.qiime_type):
                view_type = param.view_type
            else:
                view_type = list

            yield ParamTemplate(
                param.base_name + "_list",
                List[param.qiime_type],
                view_type,
                tuple(list(x) for x in underpowered_set(param.domain)))
    make_list.__name__ = 'list_' + generator.__name__
    return make_list()


def collection_paramgen(generator):
    def make_collection():
        for param in generator:
            if is_semantic_type(param.qiime_type):
                view_type = param.view_type
            else:
                view_type = dict

            yield ParamTemplate(
                param.base_name + "_collection",
                Collection[param.qiime_type],
                view_type,
                tuple({str(k): v for k, v in enumerate(x)}
                      for x in underpowered_set(param.domain)))
    make_collection.__name__ = 'collection_' + generator.__name__
    return make_collection()
