from ydc.tools.cache import cache_result
import pandas as pd


@cache_result('pickles')
def _get_stars(businesses, indices):
    return indices.apply(
        lambda row: pd.Series(businesses.iloc[row]['real_stars'].reset_index(drop=True)))


@cache_result('pickles')
def stars_stats(businesses, indices):
    data = _get_stars(businesses, indices)

    """Different statistiks for review count"""
    df_feat = pd.DataFrame()
    df_feat['stars_mean'] = data.mean(1)
    df_feat['stars_median'] = data.median(1)
    df_feat['stars_std'] = data.std(1)
    df_feat['stars_max'] = data.max(1)
    df_feat['stars_min'] = data.min(1)
    df_feat['stars_sum'] = data.sum(1)

    return df_feat
