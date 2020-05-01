# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

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


SingleIntDirectoryFormat = model.SingleFileDirectoryFormat(
    'SingleIntDirectoryFormat', 'int.txt', SingleIntFormat)
