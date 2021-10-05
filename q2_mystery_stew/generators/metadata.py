# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd

import qiime2
from qiime2.plugin import Metadata, MetadataColumn, Categorical

from q2_mystery_stew.generators.base import ParamTemplate


def metadata1():
    df = pd.DataFrame({'col1': ['a', 'b', 'c'], 'col2': ['x', 'y', 'z']},
                      index=['id1', 'id2', 'id3'])
    df.index.name = 'id'
    return qiime2.Metadata(df)


def metadata_params():
    yield ParamTemplate('metadata_cat', Metadata, qiime2.Metadata,
                        (metadata1,))
    yield ParamTemplate('column_cat', MetadataColumn[Categorical],
                        qiime2.CategoricalMetadataColumn,
                        ([metadata1, 'col1'], [metadata1, 'col2']))
