from ydc.tools.cache import cache_result
import pandas as pd
from sklearn.preprocessing import StandardScaler


@cache_result('pickles')
def _get_stars(businesses, indices):
    return indices.apply(
        lambda row: pd.Series(businesses.iloc[row]['real_stars'].reset_index(
            drop=True)))


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


@cache_result('pickles')
def rel_stars_stats(df, n_ind, combos):
    # Relative stars
    normed_stars = df[['real_stars']].copy(deep=True)
    normed_stars['norm_stars'] = 0

    # Norm each category independently
    for combo in combos:
        idx = (df['category'] == combo)
        frame_slice = normed_stars.loc[idx, 'real_stars']
        scaler = StandardScaler()
        normed_stars.loc[idx, 'norm_stars'] = scaler.fit_transform(frame_slice)

    n_new = n_ind.apply(
        lambda row: pd.Series(
            normed_stars.loc[row, 'norm_stars'].reset_index(drop=True)))

    return pd.DataFrame({
        'relative_rating_mean': n_new.mean(1),
        'relative_rating_std': n_new.std(1)
    })
