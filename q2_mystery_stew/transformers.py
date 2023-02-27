# ----------------------------------------------------------------------------
# Copyright (c) 2020-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2
from q2_mystery_stew.format import SingleIntFormat, MetadataLikeFormat


def to_single_int_format(data: int) -> SingleIntFormat:
    ff = SingleIntFormat()
    with ff.open() as fh:
        fh.write('%d\n' % data)
    return ff


def transform_to_metadata(ff: MetadataLikeFormat) -> qiime2.Metadata:
    return qiime2.Metadata.load(str(ff))


def transform_from_metatadata(data: qiime2.Metadata) -> MetadataLikeFormat:
    ff = MetadataLikeFormat()
    data.save(str(ff), ext=None)
    return ff
