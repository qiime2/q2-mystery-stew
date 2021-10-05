# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from q2_mystery_stew.format import SingleIntFormat


def to_single_int_format(data: int) -> SingleIntFormat:
    ff = SingleIntFormat()
    with ff.open() as fh:
        fh.write('%d\n' % data)
    return ff
