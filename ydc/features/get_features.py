import pandas as pd

from ydc.tools.import_data import import_businesses
from ydc.tools.distances import CellCollection
from ydc.tools.supercats import add_supercats
from ydc.tools.cache import cache_result

from ydc.features.categories import count_combo, count_super
from ydc.features.review_count import (
    review_average)
from ydc.features.distances import (
    neighbourhood_radius,
    neighbourhood_radius_squared)
from ydc.features.stars import stars_stats, rel_stars_stats


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

    # Don't do that, filter for Las Vegas instead
    # lv = df['city'] == 'Las Vegas'
    # idx = lv & -bad

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
def _simple_stats(key, df, n_ind):
    """
    Take a column of the df as a key and n_ind as indices for the neighbourhood
    The function will generate basic statistics for the column per
    neighbourhood
    """
    n_new = n_ind.apply(
        lambda row: pd.Series(
            df.loc[row, key].reset_index(drop=True)))

    return pd.DataFrame({
        '%s_mean' % key: n_new.mean(1),
        '%s_median' % key: n_new.mean(1),
        '%s_std' % key: n_new.std(1),
        '%s_max' % key: n_new.max(1),
        '%s_min' % key: n_new.min(1),
    })


@cache_result('pickles')
def distance_weighted_stats(key, df, n_ind, distances, status=False):
    def _weighted_mean(data, idx, distances, status):
        distances = pd.Series(distances.iloc[idx])
        if status:
            print("Index {}".format(idx), end='\r')
        return mean(data * 1 / (1 + distances ** 2))

    if status:
        print("Reading data", end='\r')
    data = n_ind.apply(
        lambda row: pd.Series(
            df.loc[row, key].reset_index(drop=True)))

    if status:
        print("Weight the Average", end='\r')
    weighted = data.apply(
        lambda row: _weighted_mean(row, row.index, distances, status))

    return weighted


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
        print('Neighbourhood Radius...', end='\r')
    features.append(neighbourhood_radius(n_distances, new_cache=new_cache))
    features.append(neighbourhood_radius_squared(n_distances,
                                                 new_cache=new_cache))

    if status:
        print('Stars...', end='\r')
    features.append(stars_stats(df, n_indices, new_cache=new_cache))
    features.append(
        rel_stars_stats(df, n_indices, combos, new_cache=new_cache))

    if status:
        print('Adding various smallers stats...')
    features.append(_simple_stats('lifetime', df, n_indices))
    features.append(_simple_stats('reviews_per_lifetime', df, n_indices))
    features.append(df['latitude'])
    features.append(df['longitude'])
    # features.append(_simple_stats('review_count', df, n_indices))
    # features.append(_simple_stats('review_count_last_year', df, n_indices))

    """
    if status:
        print('Reviews in the last year...', end='\r')
    features.append(last_year_reviews(df, reviews, n_indices, status,
                                      new_cache=new_cache))
    """
    # Add more!

    # Give back feature sets
    feature_sets = []
    for item in features:
        if type(item) == pd.DataFrame:
            feature_sets.append(item.columns.tolist())
        elif type(item) == pd.Series:
            feature_sets.append([item.name])

    if status:
        print('Putting all together...', end="\r")
    # Concat it all and return
    return (pd.concat(features, axis=1),
            df,
            box,
            combos,
            cells,
            n_indices,
            n_distances,
            feature_sets)
