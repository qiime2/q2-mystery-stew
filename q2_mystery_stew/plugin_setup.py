# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin import Plugin

import q2_mystery_stew

plugin = Plugin(
    name='mystery-stew',
    version=q2_mystery_stew.__version__,
    package='q2_mystery_stew',
    description=('This QIIME 2 plugin Templates out arbitrary QIIME 2 actions '
                 'to test interfaces. '),
    short_description='Plugin for generating arbitrary QIIME 2 actions.'
)
