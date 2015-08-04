import pandas as pd
import json
from os import path
from ydc.tools.cache import cache_result
import datetime as dt

DATA_PATH = 'data'
PICKLE_PATH = 'pickles'

BUSINESSES_PATH = path.join(DATA_PATH, 'yelp_academic_dataset_business.json')
CHECKINS_PATH = path.join(DATA_PATH, 'yelp_academic_dataset_checkin.json')
REVIEWS_PATH = path.join(DATA_PATH, 'yelp_academic_dataset_review.json')
TIPS_PATH = path.join(DATA_PATH, 'yelp_academic_dataset_tip.json')
USERS_PATH = path.join(DATA_PATH, 'yelp_academic_dataset_user.json')


def _get_frame(file_path, fields=None):
    data = []
    with open(file_path) as file:
        for line in file:
            line_dict = json.loads(line)
            if fields is not None:
                for key in list(line_dict.keys()):
                    if key not in fields:
                        line_dict.pop(key)
            data.append(line_dict)
    return pd.DataFrame(data)


@cache_result('pickles')
def import_reviews(status=None, fields=None):
    dataframe = _get_frame(REVIEWS_PATH, fields)
    if fields is None or 'real_date' in fields:
        assert 'date' in dataframe.columns.values
        dataframe['real_date'] = dataframe['date'].apply(
            lambda date: dt.datetime.strptime(date, '%Y-%m-%d'))
    print('Successfully imported reviews with columns {}'.format(
        dataframe.columns.values))
    return dataframe


def _one_year(date_series):
    threshold = date_series.max() - dt.timedelta(days=365)
    return (date_series > threshold).sum()


@cache_result('pickles')
def import_businesses(status=None, fields=None):
    dataframe = _get_frame(BUSINESSES_PATH, fields)
    if fields is None or 'real_stars' in fields:
        reviews = import_reviews(
            fields=['business_id', 'stars'])
        real_stars = reviews.groupby('business_id').mean()
        real_stars.columns = ['real_stars']
        dataframe = dataframe.join(real_stars, on='business_id')
    if fields is None or 'review_count_last_year' in fields:
        reviews = import_reviews(
            fields=['business_id', 'date', 'real_date'])
        grouped = reviews.groupby('business_id')['real_date'].agg(
            {'review_count_last_year': _one_year})
        # Pandas is stupid and interpreted the sum as a timestamp
        result = grouped['review_count_last_year'].apply(
            lambda x: x.nanosecond)
        dataframe = dataframe.join(result, on='business_id')

    # if fields is None or 'trend_stars' in fields:
    #    reviews = import_reviews(
    #        fields=['business_id', 'stars', 'date', 'real_date'])
    #    dataframe['trend_stars'] = review_analysis.trend_stars(
    #        dataframe['business_id'], reviews)
    if status:
        print('Successfully imported businesses with columns {}'.format(
              dataframe.columns.values))
    return dataframe


def import_checkins(status=None, fields=None):
    dataframe = _get_frame(CHECKINS_PATH, fields)
    if status:
        print('Successfully imported checkins with columns {}'.format(
              dataframe.columns.values))
    return dataframe


def import_tips(status=None, fields=None):
    dataframe = _get_frame(TIPS_PATH, fields)
    if status:
        print('Successfully imported tips with columns {}'.format(
            dataframe.columns.values))
    return dataframe


def import_users(status=None, fields=None):
    dataframe = _get_frame(USERS_PATH, fields)
    if status:
        print('Successfully imported users with columns {}'.format(
            dataframe.columns.values))
    return dataframe
