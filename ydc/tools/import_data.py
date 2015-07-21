import pandas as pd
import json
from os import path
from ydc.tools import review_analysis
from ydc.tools.cache import cache_result
import datetime as dt

DATA_PATH = 'data'
PICKLE_PATH = 'pickles'

BUSINESSES_PATH = path.join(DATA_PATH, 'yelp_academic_dataset_business.json')
CHECKINS_PATH = path.join(DATA_PATH, 'yelp_academic_dataset_checkin.json')
REVIEWS_PATH = path.join(DATA_PATH, 'yelp_academic_dataset_review.json')
TIPS_PATH = path.join(DATA_PATH, 'yelp_academic_dataset_tip.json')
USERS_PATH = path.join(DATA_PATH, 'yelp_academic_dataset_user.json')


def import_file(file_path, pickle_name):
    def decorate(func):
        def decorated(fields=None, status=False, cache=True):
            data = []
            with open(file_path) as file:
                for line in file:
                    line_dict = json.loads(line)
                    if fields is not None:
                        for key in list(line_dict.keys()):
                            if key not in fields:
                                line_dict.pop(key)
                    data.append(line_dict)
            ret = pd.DataFrame(data)
            ret = func(ret, status, fields)
            return ret
        return decorated
    return decorate


@cache_result('pickles')
@import_file(REVIEWS_PATH, 'reviews')
def import_reviews(dataframe, status, fields):
    if fields is None or 'real_date' in fields:
        assert 'date' in dataframe.columns.values
        dataframe['real_date'] = dataframe['date'].apply(
            lambda date: dt.datetime.strptime(date, '%Y-%m-%d'))
    print('Successfully imported reviews with columns {}'.format(
        dataframe.columns.values))
    return dataframe


@cache_result('pickles')
@import_file(BUSINESSES_PATH, 'businesses')
def import_businesses(dataframe, status, fields):
    if fields is None or 'real_stars' in fields:
        reviews = import_reviews(
            fields=['business_id', 'stars'])
        real_stars = reviews.groupby('business_id').mean()
        real_stars.columns = ['real_stars']
        dataframe = dataframe.join(real_stars, on='business_id')
    #if fields is None or 'trend_stars' in fields:
    #    reviews = import_reviews(
    #        fields=['business_id', 'stars', 'date', 'real_date'])
    #    dataframe['trend_stars'] = review_analysis.trend_stars(
    #        dataframe['business_id'], reviews)
    if status:
        print('Successfully imported businesses with columns {}'.format(
              dataframe.columns.values))
    return dataframe


@import_file(CHECKINS_PATH, 'checkins')
def import_checkins(dataframe, status, fields):
    if status:
        print('Successfully imported checkins with columns {}'.format(
              dataframe.columns.values))
    return dataframe


@import_file(TIPS_PATH, 'tips')
def import_tips(dataframe, status, fields):
    if status:
        print('Successfully imported tips with columns {}'.format(
            dataframe.columns.values))
    return dataframe


@import_file(USERS_PATH, 'users')
def import_users(dataframe, status, fields):
    if status:
        print('Successfully imported users with columns {}'.format(
            dataframe.columns.values))
    return dataframe
