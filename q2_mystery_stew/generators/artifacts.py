# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2

from q2_mystery_stew.type import SingleInt1, SingleInt2
from q2_mystery_stew.format import SingleIntFormat
from q2_mystery_stew.generators.base import ParamTemplate


def single_int1_1():
    return qiime2.Artifact.import_data('SingleInt1', 42)


def single_int1_2():
    return qiime2.Artifact.import_data('SingleInt1', 43)


def single_int1_3():
    return qiime2.Artifact.import_data('SingleInt1', 44)


def single_int2_1():
    return qiime2.Artifact.import_data('SingleInt2', 2019)


def single_int2_2():
    return qiime2.Artifact.import_data('SingleInt2', 2020)


def single_int2_3():
    return qiime2.Artifact.import_data('SingleInt2', 2021)


def artifact_params():
    yield ParamTemplate('simple_type1', SingleInt1, SingleIntFormat,
                        (single_int1_1, single_int1_2, single_int1_3))
    yield ParamTemplate('simple_type2', SingleInt2, SingleIntFormat,
                        (single_int2_1, single_int2_2, single_int2_3))
    yield ParamTemplate('union_type', SingleInt1 | SingleInt2, SingleIntFormat,
                        (single_int1_1, single_int2_1, single_int2_2,
                         single_int1_3))
