from geopy.distance import vincenty
from numpy import linspace
import pandas as pd


class CellCollection:

    def __init__(self, num_x, num_y):
        self.longitudes = linspace(-180, 180, num_x)
        self.latitudes = linspace(-90, 90, num_y)

    def get_cell(self, business):
        x = 0
        while x < self.longitudes.size - 1:
            if business.longitude > self.longitudes[x] and \
                    business.longitude < self.longitudes[x + 1]:
                break
            else:
                x = x + 1
        y = 0
        while y < self.latitudes.size - 1:
            if business.latitude > self.latitudes[y] and \
                    business.latitude < self.latitudes[y + 1]:
                break
            else:
                y = y + 1
        return x, y

    def get_neighbours(self, business, businesses):

        def radius_step(radius, num_longtidues, num_latitudes):
            if radius['long_down'] > 0:
                radius['long_down'] = radius['long_down'] - 1
            if radius['long_up'] < num_longtidues - 1:
                radius['long_up'] = radius['long_up'] + 1
            if radius['lat_down'] > 0:
                radius['lat_down'] = radius['lat_down'] - 1
            if radius['lat_up'] < num_latitudes - 1:
                radius['lat_up'] = radius['lat_up'] + 1

        cell = self.get_cell(business)
        radius = {'long_down': cell[0], 'long_up': cell[0] + 1,
                  'lat_down': cell[1], 'lat_up': cell[1] + 1}
        ret = []
        while len(ret) == 0:
            radius_step(radius, self.longitudes.size, self.latitudes.size)
            query = ("business_id != '{0}'and longitude > {1} "
                     "and longitude < {2} and latitude > {3} "
                     "and latitude < {4}").format(
                business.business_id,
                self.longitudes.item(radius['long_down']),
                self.longitudes.item(radius['long_up']),
                self.latitudes.item(radius['lat_down']),
                self.latitudes.item(radius['lat_up']))
            ret = businesses.query(query)
        return ret


def distance(a, b):
    """Calculate distances between businesses
    :param a: first business
    :param b: second business
    :returns: distance in meters"""
    return vincenty((a.longitude, a.latitude), (b.longitude, b.latitude)).km


def get_neighbours(business, businesses):
    cells = CellCollection(36000, 18000)
    neighbours = cells.get_neighbours(business, businesses)
    neighbours['distance'] = pd.Series(neighbours.apply(
        lambda row: distance(business, row), axis=1), index=neighbours.index)
    return neighbours


def neirest_neighbour(business, businesses):
    """Find neirest neighbour of a business
    :param business: The business we search the neirest neighbour for
    :param businesses: The DataFrame of businesses we search in
    :returns: neighbour id and distance"""
    neighbours = get_neighbours(business, businesses)
    index = neighbours['distance'].idxmin()
    print(index)
    return neighbours.loc[index]
