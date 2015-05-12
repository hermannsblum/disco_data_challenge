from geopy.distance import vincenty
from numpy import linspace
from math import exp
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


class ExponentialRadius:

    def __init__(self, step, business):
        self.i = -1
        self.long_point = float(business.longitude)
        self.lat_point = float(business.latitude)
        self.long_down = float(business.longitude)
        self.long_up = float(business.longitude)
        self.lat_down = float(business.latitude)
        self.lat_up = float(business.latitude)
        self.step_dist = float(step)

    def step(self):
        self.i = self.i + 1
        step = self.step_dist * exp(self.i)

        self.long_down = self.long_point - step
        if self.long_down < -180:
            self.long_down = -180
        self.long_up = self.long_point + step
        if self.long_up > 180:
            self.long_up = 180
        self.lat_down = self.lat_point - step
        if self.lat_down < -90:
            self.lat_down = -90
        self.lat_up = self.lat_point + step
        if self.lat_up > 90:
            self.lat_up = 90

    def inner_radius(self):
        return vincenty((self.long_point, self.lat_point), (self.long_down, self.lat_point)).km


def get_neighbours(business, businesses, num=5, step=0.1):
    """
    :param business: The business we search the neirest neighbour for
    :param businesses: The DataFrame of businesses we search in
    :param num: minimal number of neighbours to return
    :param step: distance for one search step in km
    """
    # degrees for 1km at the aquator
    onekm = 360 / 40074
    # convert step to degrees
    step = step * onekm
    radius = ExponentialRadius(step, business)
    neighbours = []
    region = []
    i = 0
    while len(neighbours) < num and radius.inner_radius() < 100:
        i = i + 1
        while len(region) < num * exp(i):
            print(radius.inner_radius())
            radius.step()
            query = ('index != "{0}" and longitude > {1} '
                     "and longitude < {2} and latitude > {3} "
                     "and latitude < {4}").format(
                business.index, radius.long_down, radius.long_up,
                radius.lat_down, radius.lat_up)
            region = businesses.query(query)

        print(radius.inner_radius())
        neighbours = region
        neighbours['distance'] = pd.Series(neighbours.apply(
            lambda row: distance(business, row), axis=1), index=neighbours.index)
        neighbours = neighbours[neighbours['distance'] < radius.inner_radius()]
    return neighbours


def distance(a, b):
    """Calculate distances between businesses
    :param a: first business
    :param b: second business
    :returns: distance in meters"""
    return vincenty((float(a.longitude), float(a.latitude)),
                    (float(b.longitude), float(b.latitude))).km


def neirest_neighbour(business, businesses):
    """Find neirest neighbour of a business
    :param business: The business we search the neirest neighbour for
    :param businesses: The DataFrame of businesses we search in
    :returns: neighbour id and distance"""
    neighbours = get_neighbours(business, businesses, num=1)
    index = neighbours['distance'].idxmin()
    return neighbours.loc[index]
