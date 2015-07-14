import datetime as dt


def last_review(business_ids, reviews):
    ret = business_ids.apply(
        lambda id: reviews[reviews['business_id'] == id].index.max()
    )
    return ret


# last possible day for reviews was 2015-01-08
END_OF_ALL_TIME = dt.date(2015, 1, 8)


def last_month_review_count(business_ids, reviews):
    one_month_ago = END_OF_ALL_TIME - dt.timedelta(days=30)
    ret = business_ids.apply(
        lambda id: reviews[(reviews['business_id'] == id) &
                           (reviews.index > one_month_ago)].count()
    )
    return ret


def last_year_review_count(business_ids, reviews):
    one_year_ago = END_OF_ALL_TIME - dt.timedelta(years=1)
    ret = business_ids.apply(
        lambda id: reviews[(reviews['business_id'] == id) &
                           (reviews.index > one_year_ago)].count()
    )
    return ret

