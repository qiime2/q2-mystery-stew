# ----------------------------------------------------------------------------
# Copyright (c) 2020-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2
from qiime2.plugin import TextFileFormat, ValidationError
import qiime2.plugin.model as model


class SingleIntFormat(TextFileFormat):
    """
    Exactly one int on a single line in the file.

    """
    def _validate_(self, level):
        with self.open() as fh:
            try:
                int(fh.readline().rstrip('\n'))
            except (TypeError, ValueError):
                raise ValidationError("File does not contain an integer")
            if fh.readline():
                raise ValidationError("Too many lines in file.")

    def get_int(self):
        with self.open() as fh:
            return int(fh.readline().rstrip('\n'))


SingleIntDirectoryFormat = model.SingleFileDirectoryFormat(
    'SingleIntDirectoryFormat', 'int.txt', SingleIntFormat)


class MetadataLikeFormat(TextFileFormat):
    """
    Just the QIIME 2 metadata format
    """
    def _validate_(self, level):
        try:
            qiime2.Metadata.load(str(self))
        except Exception as e:
            raise ValidationError(str(e))


MetadataLikeDirectoryFormat = model.SingleFileDirectoryFormat(
    'MetadataLikeDirectoryFormat', 'just-metadata.tsv', MetadataLikeFormat)


class EchoOutputFmt(model.TextFileFormat):
    def validate(self, *args):
        pass


EchoOutputDirFmt = model.SingleFileDirectoryFormat('EchoOutputDirFmt',
                                                   'echo.txt', EchoOutputFmt)
