import pandas as pd

from ydc.tools.cache import cache_result


def _indices(row, cells):
    """Find indices of 24 closest businesses"""
    nbrs = cells.get_neighbours(row, 24)
    return [item['index'] for item in nbrs]


@cache_result("pickles")
def _get_neighbourhood(df, cells):
    """Get the neighbourhood. 24 neighbours plus myself
    Caching because this neighbourhood is used in different functions
    """
    # Find 24 closest shops
    others = df.apply(lambda row: _indices(row, cells), axis=1)

    # No add own index to every list to get neighbourshoods of 25
    neighbourhoods_raw = {}
    for key in others.index:
        neighbourhoods_raw[key] = others[key] + [key]

    return pd.Series(neighbourhoods_raw)


def _cat_count(indices, df):
    """Counts occurence and divides by 25"""
    return df.iloc[indices].value_counts() / 25


@cache_result("pickles")
def neighbourhood_features(df, cells, new_neighbourhoods=False):
    nbrs = _get_neighbourhood(df, cells, new_cache=new_neighbourhoods)

    # If we use the tuples pandas gets ecited and creates a multiindex
    df_work = df['category'].astype(str)

    df_cat_feats = nbrs.apply(lambda indices: _cat_count(indices, df_work))

    # Replace NaN with 0 (0 occurences)
    df_cat_feats.fillna(0, inplace=True)

    return df_cat_feats
