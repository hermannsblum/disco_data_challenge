import pandas as pd

from ydc.tools.import_data import import_businesses
from ydc.tools.distances import CellCollection
from ydc.tools.supercats import add_supercats
from ydc.tools.cache import cache_result

from ydc.features.neighbourhood import neighbourhood_features


@cache_result("pickles")
def _get_cells(pot, df):
    """This function is just a wrapper for easy caching"""
    return CellCollection(pot, df)


def get_features(status=False, new_cache=False):
    """Imports businesses and creates a wide range of numerical features"""
    if status:
        print('Importing data...', end="\r")
    df_raw = import_businesses(new_cache=new_cache)

    if status:
        print('Categorize...', end="\r")
    (df, box, combos) = add_supercats(df_raw, new_cache=new_cache)

    if status:
        print('Sorting into cells...', end="\r")
    cells = _get_cells(16, df, new_cache=new_cache)

    # Create features here (Make sure everything is cached to save work)
    # Every feature module is a new list element
    # (to easily combine or remove them)
    features = []
    if status:
        print('Neighbourhood features...', end="\r")
    features.append(neighbourhood_features(
        df, cells, new_cache=new_cache, new_neighbourhoods=new_cache))
    # Add more!

    if status:
        print('Putting all together...', end="\r")
    # Concat it all and return
    return pd.concat(features, axis=1)
