import numpy as np
from ydc.tools.cache import cache_result


@cache_result('pickles')
def neighbourhood_radius(distances):
    ret = distances.apply(np.max)
    ret.name = 'neighbourhood_radius'
    return ret
