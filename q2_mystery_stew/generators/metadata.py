# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd

import qiime2
from qiime2.plugin import Metadata, MetadataColumn, Categorical, Numeric

from q2_mystery_stew.generators.base import ParamTemplate


def metadata1():
    df = pd.DataFrame({'col1': ['a', 'b', 'c'], 'col2': ['x', 'y', 'z']},
                      index=['id1', 'id2', 'id3'])
    df.index.name = 'id'
    return qiime2.Metadata(df)


def metadata2():
    df = pd.DataFrame({'col3': [1, 2, 3], 'col4': [0.1, 0.01, 0.001]},
                      index=['id1', 'id2', 'id3'])
    df.index.name = 'id'
    return qiime2.Metadata(df)


def artifact_cat():
    return qiime2.Artifact.import_data('BasicallyMetadata', metadata1())


def artifact_num():
    return qiime2.Artifact.import_data('BasicallyMetadata', metadata2())


def metadata_params():
    yield ParamTemplate('metadata', Metadata, qiime2.Metadata,
                        (metadata1, metadata2, artifact_cat, artifact_num,
                         [metadata1, metadata2],
                         [metadata1, artifact_num],
                         [artifact_cat, metadata2],
                         [artifact_cat, artifact_num]))
    yield ParamTemplate('column_cat', MetadataColumn[Categorical],
                        qiime2.CategoricalMetadataColumn,
                        ([metadata1, 'col1'], [metadata1, 'col2'],
                         [artifact_cat, 'col1'], [artifact_cat, 'col2']))
    yield ParamTemplate('column_num', MetadataColumn[Numeric],
                        qiime2.NumericMetadataColumn,
                        ([metadata2, 'col3'], [metadata2, 'col4'],
                         [artifact_num, 'col3'], [artifact_num, 'col4']))
    yield ParamTemplate('column_any', MetadataColumn[Categorical | Numeric],
                        qiime2.MetadataColumn,
                        ([metadata1, 'col1'], [metadata2, 'col4'],
                         [artifact_cat, 'col2'], [artifact_num, 'col3']))
