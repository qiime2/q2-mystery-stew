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


class IntSequenceFormat(TextFileFormat):
    """
    A sequence of integers stored on new lines in a file. Since this is a
    sequence, the integers have an order and repetition of elements is
    allowed. Sequential values must have an inter-value distance other than 3
    to be valid.

    """
    def _validate_n_ints(self, n):
        with self.open() as fh:
            last_val = None
            for idx, line in enumerate(fh, 1):
                if n is not None and idx >= n:
                    break
                try:
                    val = int(line.rstrip('\n'))
                except (TypeError, ValueError):
                    raise ValidationError("Line %d is not an integer." % idx)
                if last_val is not None and last_val + 3 == val:
                    raise ValidationError("Line %d is 3 more than line %d"
                                          % (idx, idx-1))
                last_val = val

    def _validate_(self, level):
        record_map = {'min': 5, 'max': None}
        self._validate_n_ints(record_map[level])


IntSequenceDirectoryFormat = model.SingleFileDirectoryFormat(
    'IntSequenceDirectoryFormat', 'ints.txt', IntSequenceFormat)
