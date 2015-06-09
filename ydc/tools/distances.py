from geopy.distance import vincenty
from numpy import linspace
from math import exp
import pandas as pd


class CellCollection:

    def __init__(self, potenz, businesses):
        """Create CellCollection
        :param potenz: The CellCollection has dimension 2^(potenz+1) x 2^potenz
        :param businesses: The businesses stored in these Cells
        :returns: CellCollection"""

        def fill_cells(self, latitudes, longitudes, businesses):
            """Sort the businesses into the cells recursively
            :param latitudes: the nparray of longitudes in the cell-grid
            :param latitudes: the nparray of latitudes in the cell-grid
            :param businesses: the DataFrame of businesses to sort into this
                CellCollection
            :returns: The CellCollection as dict of dicts. Keys are the inizes
                in the longitudes and latitudes arrays of the lower left point
                of a cell"""
            if len(businesses) == 0:
                # There are no businesses in this area
                return
            if longitudes.size > 2:
                # First we devide the collection along the center of longitudes
                center = longitudes[len(longitudes) / 2]
                fill_cells(self, latitudes,
                           longitudes[:(longitudes.size / 2 + 1)],
                           businesses[businesses.longitude <= center])
                fill_cells(self, latitudes, longitudes[(longitudes.size / 2):],
                           businesses[businesses.longitude > center])
            elif latitudes.size > 2:
                # Now we devide along the center of latitudes
                center = latitudes[latitudes.size / 2]
                fill_cells(self, latitudes[:(latitudes.size / 2 + 1)],
                           longitudes,
                           businesses[businesses.latitude <= center])
                fill_cells(self, latitudes[(latitudes.size / 2):], longitudes,
                           businesses[businesses.latitude > center])
            else:
                # Now we are in one Cell! Let's store our businesses
                bizs = []
                for idx, business in businesses.iterrows():
                    # For performance, we only store index and coordinates
                    bizs.append({'index': idx,
                                 'latitude': business.latitude,
                                 'longitude': business.longitude})
                coord = (self.longitudes.searchsorted(longitudes[0]),
                         self.latitudes.searchsorted(latitudes[0]))
                if coord[0] not in self.cells:
                    self.cells[coord[0]] = {}
                if len(bizs) > 0:
                    # We don't need empty entries
                    self.cells[coord[0]].update({coord[1]: bizs})

        self.longitudes = linspace(-180, 180, (2 ** (potenz + 1)) + 1)
        self.latitudes = linspace(-90, 90, (2 ** potenz) + 1)

        # fill the cells of our new array
        self.cells = {}
        fill_cells(self, self.latitudes, self.longitudes, businesses)

    def get_cell(self, business):
        """Finds the Cell the given businesses would belong to
        :returns: Coordinates as a Tuple"""
        x = self.longitudes.searchsorted(business.longitude)
        y = self.latitudes.searchsorted(business.latitude)
        return x, y

    def get_neighbours(self, business, num=5):
        """Finds neighbours of a given business
        :param business: the business we search neighbours for
        :param num: minimum-number of neighbours returnes, default 5
        :returns: list of dicts with 'index', 'latitude', 'longitude',
            'distance'"""

        def radius_step(radius, num_longtidues, num_latitudes, time):
            """expand the search-radius exponentially"""
            step = int(exp(time))
            radius['long_down'] = radius['long_down'] - step
            if radius['long_down'] <= 0:
                radius['long_down'] = 0
            radius['long_up'] = radius['long_up'] + step
            if radius['long_up'] >= num_longtidues - 1:
                radius['long_up'] = num_longtidues - 1
            radius['lat_down'] = radius['lat_down'] - step
            if radius['lat_down'] <= 0:
                radius['lat_down'] = 0
            radius['lat_up'] = radius['lat_up'] + step
            if radius['lat_up'] >= num_latitudes - 1:
                radius['lat_up'] = num_latitudes - 1

        cell = self.get_cell(business)
        radius = {'long_down': cell[0], 'long_up': cell[0] + 1,
                  'lat_down': cell[1], 'lat_up': cell[1] + 1}
        ret = []
        time = 0
        inner_radius = 0
        while len(ret) < num and inner_radius < 100:
            ret = []
            found = []
            radius_step(radius, self.longitudes.size, self.latitudes.size,
                        time)
            for row in range(radius['long_down'], radius['long_up']):
                for col in range(radius['lat_down'], radius['lat_up']):
                    if row in self.cells and col in self.cells[row]:
                        for item in self.cells[row][col]:
                            found.append(item)
            # We approximate the in-radius of the search-rectangle by half of
            # the distance between the centers of left and right border
            # (Not exactly the in-radius on the surface of a sphereoid, but
            # easier to calculate)
            inner_radius = vincenty((self.longitudes[radius['long_down']],
                                     self.latitudes[cell[1]]),
                                    (self.longitudes[radius['long_up']],
                                     self.latitudes[cell[1]])).km / 2
            for neighbour in found:
                dist = vincenty((business.longitude, business.latitude),
                                (neighbour['longitude'], neighbour['latitude'])
                                ).km
                # make sure we only include businesses in the in-circle of the
                # search-rectangle
                if dist <= inner_radius and \
                        neighbour['index'] != business.name:
                    neighbour['distance'] = dist
                    ret.append(neighbour)
        return ret

    def to_dataframe(self):
        ret = pd.DataFrame(self.cells)
        return ret

    def to_dict(self):
        return self.cells.copy()

    def get_borders(self):
        return self.longitudes.copy(), self.latitudes.copy()


def distance(a, b):
    """Calculate distances between businesses
    :param a: first business
    :param b: second business
    :returns: distance in meters"""
    return vincenty((float(a.longitude), float(a.latitude)),
                    (float(b.longitude), float(b.latitude))).km


def neirest_neighbour(business, cells):
    """Find neirest neighbour of a business
    :param business: The business we search the neirest neighbour for
    :param businesses: The DataFrame of businesses we search in
    :returns: neighbour id and distance"""
    array = cells.get_neighbours(business, num=1)
    neighbours = pd.DataFrame(array).set_index('index')
    index = neighbours['distance'].idxmin()
    return neighbours.loc[index]
