


def filter_usa(businesses):
    assert 'longitude' in businesses.columns.values
    assert 'latitude' in businesses.columns.values
    return businesses[(businesses['longitude'] >= 68) &
                      (businesses['longitude'] <= 125) &
                      (businesses['latitude'] >= 24) &
                      (businesses['latitude'] <= 49)]
