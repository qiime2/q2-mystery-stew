# ----------------------------------------------------------------------------
# Copyright (c) 2020-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import Int, Range, Float, Bool, Str, Choices

from q2_mystery_stew.generators.base import ParamTemplate


def int_params():
    yield ParamTemplate('single_int', Int, int, (-1, 0, 1))
    yield ParamTemplate('int_range_1_param', Int % Range(3), int, (-42, 0, 2))
    yield ParamTemplate('int_range_1_param_i_e',
                        Int % Range(3, inclusive_end=True), int, (-43, 0, 3))
    yield ParamTemplate('int_range_2_params',
                        Int % Range(-3, 4), int, (-3, 0, 3))
    yield ParamTemplate('int_range_2_params_i_e',
                        Int % Range(-3, 4, inclusive_end=True), int,
                        (-3, 0, 4))
    yield ParamTemplate('int_range_2_params_no_i',
                        Int % Range(-3, 4, inclusive_start=False), int,
                        (-2, 0, 3))
    yield ParamTemplate('int_range_2_params_i_e_ex_s',
                        Int % Range(-3, 4, inclusive_start=False,
                                    inclusive_end=True),
                        int, (-2, 0, 4))


def float_params():
    yield ParamTemplate('single_float', Float, float, (-1.5, 0.0, 1.5))
    yield ParamTemplate('float_range_1_param', Float % Range(2.5), float,
                        (-42.5, 0.0, 2.49))
    yield ParamTemplate('float_range_1_param_i_e',
                        Float % Range(2.5, inclusive_end=True), float,
                        (-42.5, 0.0, 2.5))
    yield ParamTemplate('float_range_2_params', Float % Range(-3.5, 3.5),
                        float, (-3.5, 0.0, 3.49))
    yield ParamTemplate('float_range_2_params_i_e',
                        Float % Range(-3.5, 3.5, inclusive_end=True), float,
                        (-3.5, 0.0, 3.5))
    yield ParamTemplate('float_range_2_params_no_i',
                        Float % Range(-3.5, 3.5, inclusive_start=False), float,
                        (-3.49, 0.0, 3.49))
    yield ParamTemplate('float_range_2_params_i_e_ex_s',
                        Float % Range(-3.5, 3.5, inclusive_start=False,
                                      inclusive_end=True), float,
                        (-3.49, 0.0, 3.49))


def string_params():
    # TODO: should '' be in this list?
    mean_choices = ('None', '-1', 'True', 'False', '<[^#^]>')
    yield ParamTemplate('string', Str, str, mean_choices)
    yield ParamTemplate('string_choices', Str % Choices(*mean_choices),
                        str, mean_choices)


def bool_params():
    yield ParamTemplate('boolean',
                        Bool, bool, (True, False))
    yield ParamTemplate('boolean_true',
                        Bool % Choices(True), bool, (True,))
    yield ParamTemplate('boolean_false',
                        Bool % Choices(False), bool, (False,))
    yield ParamTemplate('boolean_choice',
                        Bool % Choices(True, False), bool, (True, False))


def primitive_union_params():
    yield ParamTemplate('disjoint', Int % (Range(5, 10) | Range(15, 20)),
                        int, (5, 9, 15, 19))
    yield ParamTemplate('auto_int',
                        Int % Range(1, None) | Str % Choices('auto'),
                        object, (1, 10, 'auto'))
    yield ParamTemplate('kitchen_sink',
                        (Float % Range(0, 1) | Int |
                         Str % Choices('auto', 'Beef') | Bool |
                         Float % Range(10, 11)),
                        object, (0.5, 1000, 'Beef', 'auto', True, False,
                                 10.103))
