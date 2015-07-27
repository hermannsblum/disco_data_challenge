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

@cache_result('pickles')
def last_year_reviews(businesses, reviews, indices, status):

    def _search_last_year(reviews, bids, status):
        container = []
        if status:
            print('index {}'.format(bids.name), end='\r')
        print(bids)
        for bid in bids:
            if status:
                print('index {}, business {}'.format(bids.name, bid), end='\r')
            business_reviews = reviews[reviews['business_id'] == bid]
            last_review = business_reviews['real_date'].max()
            container.append(
                business_reviews[business_reviews['real_date'] > \
                (last_review - dt.timedelta(days=365))].count())
        return np.mean(container)

    neighbour_ids = _neighbour_ids(businesses, indices)

    last_year_reviewcount = neighbour_ids.apply(
        lambda row: _search_last_year(reviews, row, status))

    last_year_reviewcount.name = 'Reviews Last Year'

    return last_year_reviewcount

