from ydc.tools.cache import cache_result
import pandas as pd


def _rev_count(indices, df):
    """Different statistiks for review count"""
    data = df.ix[indices]
    return (data.mean(),
            data.median(),
            data.std(),
            data.max(),
            data.min(),
            data.sum())


@cache_result("pickles")
def count_rev(df, nbrs):
    # If we use the tuples pandas gets ecited and creates a multiindex
    df_work = df['review_count']

    df_feats = nbrs.apply(lambda indices: _rev_count(indices, df_work))

    # Replace NaN with 0 (0 occurences)
    df_feats.fillna(0, inplace=True)

    # Make Frame
    data = list(zip(*df_feats))
    cols = ['reviews_mean',
            'reviews_median',
            'reviews_std',
            'reviews_max',
            'reviews_min',
            'reviews_sum']
    res = pd.DataFrame(data).transpose()
    res.columns = cols

    return res
