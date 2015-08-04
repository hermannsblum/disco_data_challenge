from ydc.tools.cache import cache_result
import pandas as pd
import numpy as np
import datetime as dt


@cache_result('pickles')
def _count_reviews(businesses, indices):
    return indices.apply(
        lambda row: pd.Series(businesses.iloc[row]['review_count'].reset_index(drop=True)))


@cache_result('pickles')
def _neighbour_ids(businesses, indices):
    return indices.apply(
        lambda row: businesses.iloc[row]['business_id'].reset_index(drop=True))


@cache_result("pickles")
def count_rev(df, indices):
    # If we use the tuples pandas gets ecited and creates a multiindex

    data = _count_reviews(df, indices)

    """Different statistiks for review count"""
    df_feat = pd.DataFrame()
    df_feat['reviews_mean'] = data.mean(1)
    df_feat['reviews_median'] = data.median(1)
    df_feat['reviews_std'] = data.std(1)
    df_feat['reviews_max'] = data.max(1)
    df_feat['reviews_min'] = data.min(1)
    df_feat['reviews_sum'] = data.sum(1)

    return df_feat


@cache_result('pickles')
def review_average(businesses, indices, distances, status):
    def _mean_reviews(review_counts, idx, dist, status):
        distances = pd.Series(dist.iloc[idx])
        if status:
            print("Index {}".format(idx), end='\r')
        return np.mean(review_counts * np.exp(-1 * distances))

    if status:
        print("Counting reviews", end='\r')
    review_counts = _count_reviews(businesses, indices)

    if status:
        print("Find the Average", end='\r')
    average_review_count = review_counts.apply(
        lambda row: _mean_reviews(row.values, row.name, distances, status),
        axis=1)

    average_review_count.name = 'weighted review-count'

    return average_review_count.fillna(0)
