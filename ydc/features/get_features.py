import pandas as pd

from ydc.tools.import_data import import_businesses, import_reviews
from ydc.tools.distances import CellCollection
from ydc.tools.supercats import add_supercats
from ydc.tools.cache import cache_result

from ydc.features.categories import count_combo, count_super
from ydc.features.review_count import (
    count_rev,
    review_average,
    last_year_reviews)
from ydc.features.distances import (
    neighbourhood_radius,
    neighbourhood_radius_squared)
from ydc.features.stars import stars_stats


def _offset(df):
    return pd.Series(1, index=df.index)


def _filter_busi(df, top, bottom, left, right, count):
    r = df['longitude'] <= right
    l = df['longitude'] >= left
    t = df['latitude'] <= top
    b = df['latitude'] >= bottom

    c = df['review_count'] >= count

    bad = df['real_stars'].isnull()

    idx = r & l & t & b & c & -bad

    # Copy old and reindex
    res = df[idx].copy(deep=True)
    res.index = range(len(res.index))

    return res


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
    reviews = import_reviews(
        fields=['business_id', 'stars', 'date', 'real_date'],
        new_cache=new_cache)

    if status:
        print('Filtering businesses...', end="\r")
    top = 49     # U
    bottom = 25  # S
    left = -130  # A
    right = -65  # FUCK YEAH, MURICA
    count = 0
    df_filtered = _filter_busi(df_raw, top, bottom, left, right, count)

    if status:
        print('Categorize...', end="\r")
    (df, box, combos) = add_supercats(df_filtered, new_cache=new_cache)

    if status:
        print('Sorting into cells...', end="\r")
    cells = _get_cells(16, df, new_cache=new_cache)

    if status:
        print('Finding neighbourhoods of size 25...', end="\r")
    (n_indices, n_distances) = _get_neighbourhoods(
        df, cells, 25, new_cache=new_cache)

    # Create features here (Make sure everything is cached to save work)
    # Every feature module is a new list element
    # (to easily combine or remove them)
    features = []

    if status:
        print('Average Weighted Reviews', end='\r')
    features.append(review_average(df, n_indices, n_distances, status,
                                   new_cache=new_cache))

    if status:
        print('Category features...', end="\r")
    features.append(count_combo(df, n_indices, new_cache=new_cache))
    features.append(count_super(df, n_indices, new_cache=new_cache))

    if status:
        print('Review features...', end="\r")
    features.append(count_rev(df, n_indices, new_cache=new_cache))

    if status:
        print('Neighbourhood Radius...', end='\r')
    features.append(neighbourhood_radius(n_distances, new_cache=new_cache))
    features.append(neighbourhood_radius_squared(n_distances,
                                                 new_cache=new_cache))

    if status:
        print('Stars...', end='\r')
    features.append(stars_stats(df, n_indices, new_cache=new_cache))

    """
    if status:
        print('Reviews in the last year...', end='\r')
    features.append(last_year_reviews(df, reviews, n_indices, status,
                                      new_cache=new_cache))
    """
    # Add more!
    """
    df['last_year'] = last_year_reviews(
        df, reviews, n_indices, status, new_cache=new_cache)
    """
    if status:
        print('Putting all together...', end="\r")
    # Concat it all and return
    return (pd.concat(features, axis=1),
            df,
            box,
            combos,
            cells,
            n_indices,
            n_distances)
