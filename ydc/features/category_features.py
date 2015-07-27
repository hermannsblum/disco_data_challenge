from ydc.tools.cache import cache_result
from numpy import mean, exp
import pandas as pd


def _cat_count(indices, df):
    """Counts occurence and divides by number of businesses in neighbourhood"""
    return df.iloc[indices].value_counts() / 25


@cache_result('pickles')
def _count_reviews(businesses, indices):
    return indices.apply(
        lambda row: pd.Series([businesses.iloc[index]['review_count'] \
                               for index in indices]))


@cache_result('pickles')
def _neighbour_cats(category, indices):
    return indices.apply(
        lambda row: pd.Series([category.iloc[index].astype(str) for index in indices]))


@cache_result('pickles')
def _neighbours_supercats(super_category, indices):
    return indices.apply(
        lambda row: pd.Series([super_category.iloc[index].astype(str) for index in indices]))


@cache_result("pickles")
def count_combo(df, nbrs, new_neighbourhoods=False):
    # If we use the tuples pandas gets ecited and creates a multiindex
    df_work = df['category'].astype(str)

    df_cat_feats = nbrs.apply(lambda indices: _cat_count(indices, df_work))

    # Replace NaN with 0 (0 occurences)
    df_cat_feats.fillna(0, inplace=True)

    return df_cat_feats


@cache_result('pickles')
def review_average(businesses, indices, distances, status):
    def _mean_reviews(review_counts, idx, distances, status):
        distances = pd.Series(distances.iloc[idx])
        if status:
            print("Index {}".format(idx), end='\r')
        return mean(review_counts * exp(-distances))

    if status:
        print("Counting reviews", end='\r')
    review_counts = _count_reviews(businesses, indices)

    if status:
        print("Find the Average", end='\r')
    average_review_count = review_counts.apply(
        lambda row: _mean_reviews(row, row.index, distances, status))

    return average_review_count.fillna(0)


@cache_result('pickles')
def review_average_by_supercat(businesses, indices):
    supercats = _neighbours_supercats(businesses['super_category'], indices)
    review_counts = _count_reviews(businesses, indices)
    return review_counts.apply(
        lambda row: row.groupby(supercats.iloc[row.index]).mean())


