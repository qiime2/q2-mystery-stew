# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2.plugin as plugin

SingleInt = plugin.SemanticType('SingleInt')
IntSequence = plugin.SemanticType('IntSequence')

IntWrapper = plugin.SemanticType('IntWrapper', field_names='first')
TwoIntWrapper = \
    plugin.SemanticType('TwoIntWrapper', field_names=['first', 'second'])

_variants = [
    IntWrapper.field['first'],
    TwoIntWrapper.field['first'], TwoIntWrapper.field['second'],
]

WrappedInt = plugin.SemanticType('WrappedInt', variant_of=_variants)
