import pandas as pd
import json


DATA_PATH = 'data'

BUSINESSES_PATH = DATA_PATH + '/yelp_academic_dataset_business.json'
CHECKINS_PATH = DATA_PATH + '/yelp_academic_dataset_checkin.json'
REVIEWS_PATH = DATA_PATH + '/yelp_academic_dataset_review.json'
TIPS_PATH = DATA_PATH + '/yelp_academic_dataset_tip.json'
USERS_PATH = DATA_PATH + '/yelp_academic_dataset_user.json'


def import_file(path):
    def decorate(func):
        def decorated(status=False):
            data = []
            with open(path) as file:
                for line in file:
                    data.append(json.loads(line))
            ret = pd.DataFrame(data)
            if status:
                func(ret.columns.values)
            return ret
        return decorated
    return decorate


@import_file(BUSINESSES_PATH)
def import_businesses(columns):
    print('Successfully imported businesses with columns %s' % columns)


@import_file(CHECKINS_PATH)
def import_checkins(columns):
    print('Successfully imported checkins with columns %s' % columns)


@import_file(REVIEWS_PATH)
def import_reviews(columns):
    print('Successfully imported reviews with columns %s' % columns)


@import_file(TIPS_PATH)
def import_tips(columns):
    print('Successfully imported tips with columns %s' % columns)


@import_file(USERS_PATH)
def import_users(columns):
    print('Successfully imported users with columns %s' % columns)
