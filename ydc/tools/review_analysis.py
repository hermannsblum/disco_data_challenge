import datetime as dt
import numpy as np
from ydc.tools.cache import cache_result

"""
@cache_result('pickles')
def _calculate_real_stars():
    reviews = import_reviews(fields=['business_id', 'stars'])
    businesses = impo
    real_stars = reviews.groupby('business_id').mean()
    real_stars.columns = ['real_stars']
    dataframe = dataframe.join(real_stars, on='business_id')

@cache_result('pickles')
def real_stars(business_ids, reviews):
    ret = reviews.groupby('business_id').mean()
"""

@cache_result('pickles')
def trend_stars(business_ids, reviews):
    return business_ids.apply(
        lambda bid: trend_average(reviews, bid)[1])


def trend_average(reviews, bid, frame_radius=30, days_back=150, step_width=5):
    business_reviews = reviews[reviews['business_id'] == bid]
    # with less than 50 reviews a trend-analysis does not make sense
    last_review = business_reviews.index.max()
    if business_reviews[business_reviews.index > last_review
                        - dt.timedelta(days=days_back + 2 * frame_radius)
                        ]['business_id'].count() < 50:
        return (days_back, business_reviews['stars'].mean())
    steps = range(frame_radius, days_back + 1, step_width)
    for days_in_past in steps:
        sep_date = last_review - dt.timedelta(days=days_in_past)
        first_frame_border = sep_date + dt.timedelta(days=frame_radius)
        last_frame_border = sep_date - dt.timedelta(days=frame_radius)

        seperation = business_reviews[(business_reviews.index >= sep_date) &
                                      (business_reviews.index <= first_frame_border)]['stars'].mean() \
            - business_reviews[(business_reviews.index < sep_date) &
                               (business_reviews.index >= last_frame_border)
                               ]['stars'].mean()
        # 0.5 is our random magic number for a relevant trend cut
        if np.abs(seperation) > 0.5:
            days_back = days_in_past
            break
    return (days_back,
            business_reviews[business_reviews.index > last_review
                             - dt.timedelta(days=days_in_past)
                             ]['stars'].mean())
