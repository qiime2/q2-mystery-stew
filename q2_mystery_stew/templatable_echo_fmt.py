# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin import SemanticType, model

EchoOutput = SemanticType('EchoOutput')


class EchoOutputFmt(model.TextFileFormat):
    def validate(self, *args):
        pass


EchoOutputDirFmt = model.SingleFileDirectoryFormat('EchoOutputDirFmt',
                                                   'stats.tsv', EchoOutputFmt)
