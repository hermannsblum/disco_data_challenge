from ydc.tools.cache import cache_result


def _cat_count(indices, df):
    """Counts occurence and divides by number of businesses in neighbourhood"""
    return df.iloc[indices].value_counts() / 25


@cache_result("pickles")
def count_combo(df, nbrs, new_neighbourhoods=False):
    # If we use the tuples pandas gets ecited and creates a multiindex
    df_work = df['category'].astype(str)

    df_cat_feats = nbrs.apply(lambda indices: _cat_count(indices, df_work))

    # Replace NaN with 0 (0 occurences)
    df_cat_feats.fillna(0, inplace=True)

    return df_cat_feats
