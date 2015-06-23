import pandas as pd
import json
from os import path, makedirs
import hashlib

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
            pickle_hash = hashlib.md5()
            pickle_hash.update(bytes(pickle_name, 'UTF-8'))
            pickle_hash.update(bytes(str(fields), 'UTF-8'))
            pickle = path.join(PICKLE_PATH, pickle_hash.hexdigest() + '.pkl')
            try:
                # Try to read from pickle
                ret = pd.read_pickle(pickle)
            except FileNotFoundError as e:
                # Pickle not found, create from data file
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
                # Save pickle
                if cache:
                    makedirs(PICKLE_PATH, exist_ok=True)  # Create if necessary
                    ret.to_pickle(pickle)

            if status:
                func(ret.columns.values)
            return ret
        return decorated
    return decorate


@import_file(BUSINESSES_PATH, 'businesses')
def import_businesses(columns):
    print('Successfully imported businesses with columns %s' % columns)


@import_file(CHECKINS_PATH, 'checkins')
def import_checkins(columns):
    print('Successfully imported checkins with columns %s' % columns)


@import_file(REVIEWS_PATH, 'reviews')
def import_reviews(columns):
    print('Successfully imported reviews with columns %s' % columns)


@import_file(TIPS_PATH, 'tips')
def import_tips(columns):
    print('Successfully imported tips with columns %s' % columns)


@import_file(USERS_PATH, 'users')
def import_users(columns):
    print('Successfully imported users with columns %s' % columns)
