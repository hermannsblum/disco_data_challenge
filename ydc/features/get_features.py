import pandas as pd

from ydc.tools.import_data import import_businesses
from ydc.tools.distances import CellCollection
from ydc.tools.supercats import add_supercats
from ydc.tools.cache import cache_result

from ydc.features.category_features import count_combo, review_average


@cache_result("pickles")
def _get_neighbourhoods(df, cells, n):
    """Get the neighbourhood. N businesses in total
    Caching because this neighbourhood is used in different functions
    """
    
    def _indices(nbrs):
        return [item['index'] for item in nbrs]

    def _distances(nbrs):
        return [item['distance'] for item in nbrs]
    
    # get n-1 closest businesses + the business itself
    nbrs = df.apply(
        lambda row: cells.get_neighbours(row, num=n, add_self=True),
        axis=1
    )

    nbrs = pd.Series(nbrs)

    return nbrs.apply(_indices), nbrs.apply(_distances)


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

    if status:
        print('Finding neighbourhoods of size 25...', end="\r")
    (n_indices, n_distances) = _get_neighbourhoods(df, cells, 25, new_cache=new_cache)

    # Create features here (Make sure everything is cached to save work)
    # Every feature module is a new list element
    # (to easily combine or remove them)
    features = []
    """
    if status:
        print('Neighbourhood features...', end="\r")
    features.append(count_combo(
        df, neighbourhood, new_cache=new_cache, new_neighbourhoods=new_cache))
    """
    if status:
        print('Average Weighted Reviews', end='\r')
    features.append(review_average(df, n_indices, n_distances, status))

    if status:
        print('Putting all together...', end="\r")
    # Concat it all and return
    return (pd.concat(features, axis=1),
            df,
            box,
            combos,
            cells,
            neighbourhood)
