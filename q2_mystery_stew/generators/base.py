# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from collections import namedtuple

ParamTemplate = namedtuple('ParamTemplate', ['base_name', 'qiime_type',
                                             'view_type', 'domain'])
