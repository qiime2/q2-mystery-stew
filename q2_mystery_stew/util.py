import numpy as np


def reservoir_sampling(iterator, n, seed=42):
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
