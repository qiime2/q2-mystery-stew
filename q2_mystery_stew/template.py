# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import inspect

from q2_mystery_stew.templatable_echo_fmt import outputFileFmt


class TemplatableCallable:
    def __init__(self, input_, params, output, name):
        self.input_ = input_
        self.params = params
        self.output = output

        input_params = [inspect.Parameter(name,
                        inspect.Parameter.POSITIONAL_ONLY,
                        annotation=type_)
                        for name, type_ in input_.items()]
        input_params.extend([inspect.Parameter(name,
                             inspect.Parameter.POSITIONAL_ONLY,
                             annotation=type_)
                             for name, type_ in params.items()])

        self.__call__.__func__.__signature__ = \
            inspect.Signature(input_params, return_annotation=output)

        annotations = input_
        annotations.update(params)
        annotations.update({'return': output})

        self.__call__.__func__.__annotations__ = annotations
        self.__call__.__func__.__name__ = name

    def __call__(**kwargs):
        return outputFileFmt()
