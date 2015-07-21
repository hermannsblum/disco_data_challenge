from ydc.tools.cache import cache_result


def _cat_count(indices, df):
    """Counts occurence and divides by number of businesses in neighbourhood"""
    return df[indices].value_counts() / 25


@cache_result("pickles")
def count_combo(df, nbrs):
    # If we use the tuples pandas gets ecited and creates a multiindex
    df_work = df['category'].astype(str)

    df_cat_feats = nbrs.apply(lambda indices: _cat_count(indices, df_work))

    # Replace NaN with 0 (0 occurences)
    df_cat_feats.fillna(0, inplace=True)

    return df_cat_feats


@cache_result("pickles")
def count_super(df, nbrs):
    # If we use the tuples pandas gets ecited and creates a multiindex
    df_work = df['super_category'].astype(str)

    df_cat_feats = nbrs.apply(lambda indices: _cat_count(indices, df_work))

    # Replace NaN with 0 (0 occurences)
    df_cat_feats.fillna(0, inplace=True)

    return df_cat_feats
