# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import numpy as np


# TODO: this may be broken, should sample a consecutive array and test the dist
def reservoir_sampler(iterator, n, seed=42):
    if n is None:
        yield from iterator
        return

    if seed is not None:
        np.random.seed(seed)

    iterator = iter(iterator)
    reservoir = []

    for i in range(n):
        try:
            reservoir.append(next(iterator))
        except StopIteration:
            yield from reservoir
            return

    for element in iterator:
        skip = np.random.geometric(1/n)

        for _ in range(skip):
            try:
                element = next(iterator)
            except StopIteration:
                break
        else:
            reservoir[np.random.randint(0, n)] = element

    yield from reservoir
