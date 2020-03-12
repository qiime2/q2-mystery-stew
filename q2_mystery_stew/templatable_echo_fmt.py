# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin import SemanticType, model

from q2_mystery_stew.plugin_setup import plugin


outputFile = SemanticType('outputFile')


class outputFileFmt(model.TextFileFormat):
    def validate(self, *args):
        pass


outputFileDirFmt = model.SingleFileDirectoryFormat('outputFileDirFmt',
                                                   'stats.tsv', outputFileFmt)

plugin.register_formats(outputFileFmt, outputFileDirFmt)
plugin.register_semantic_types(outputFile)
plugin.register_semantic_type_to_format(outputFile, outputFileDirFmt)
