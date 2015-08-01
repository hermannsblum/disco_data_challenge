import numpy as np
from ydc.tools.cache import cache_result


@cache_result('pickles')
def neighbourhood_radius(distances):
    ret = distances.apply(np.max)
    ret.name = 'neighbourhood_radius'
    return ret


def neighbourhood_radius_squared(distances, new_cache):
    """Use radius function and just square the results"""
    ret = neighbourhood_radius(distances, new_cache=new_cache)
    ret.name = 'neighbourhood_radius_squared'

    return ret ** 2  # Square it!
