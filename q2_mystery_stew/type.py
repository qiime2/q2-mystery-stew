# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType


EchoOutput = SemanticType('EchoOutput')
EchoOutputBranch1 = SemanticType('EchoOutputBranch1')
EchoOutputBranch2 = SemanticType('EchoOutputBranch2')
EchoOutputBranch3 = SemanticType('EchoOutputBranch3')


SingleInt1 = SemanticType('SingleInt1')
SingleInt2 = SemanticType('SingleInt2')


IntWrapper = SemanticType('IntWrapper', field_names='first')
_variant = IntWrapper.field['first']
WrappedInt1 = SemanticType('WrappedInt1', variant_of=_variant)
WrappedInt2 = SemanticType('WrappedInt2', variant_of=_variant)
