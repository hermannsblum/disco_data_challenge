import pandas as pd
from geopy.distance import vincenty


class CellCollection:

    def __init__(self, num_x, num_y, businesses):

        def businesses_in_cell(self, x, y, businesses):
            ret = []
            for business in businesses['longitude' >= self.longitudes[x],
                                       'longitude' < self.longitudes[x + 1],
                                       'latitude' >= self.latitudes[y],
                                       'latitude' < self.latitudes[y + 1]]:
                ret.append({'id': business.business_id,
                            'latitude': business.latitude,
                            'longitude': business.longitude})
            return ret

        self.longitudes = range(-180, 180, 360 / num_x)
        self.latitudes = range(-90, 90, 180 / num_y)

        # fill the cells of our new array
        for x in xrange(num_x):
            self.cells.append([])
            for y in xrange(num_y):
                self.cells[x].append(businesses_in_cell(x, y, businesses))

    def get_cell(self, business):
        x = 0
        while business.longitude < self.longitudes[x]:
            x = x + 1
        y = 0
        while business.latitude < self.latitudes[y]:
            y = y + 1
        return x, y

    def get_businesses(self, cell_x, cell_y):
        return self.cells[cell_x][cell_y]

    def get_neighbours(self, cell_x, cell_y):
        ret = []
        neighbours = [[cell_x - 1, cell_y - 1],
                      [cell_x, cell_y - 1],
                      [cell_x + 1, cell_y - 1],
                      [cell_x - 1, cell_y],
                      [cell_x, cell_y],
                      [cell_x + 1, cell_y],
                      [cell_x - 1, cell_y + 1],
                      [cell_x, cell_y + 1],
                      [cell_x + 1, cell_y + 1]]
        for neighbour in neighbours:
            if neighbour[0] >= 0 and neighbour[1] >= 0:
                ret.append(self.cells[neighbour[0]][neighbour[1]])
        return ret


def distance(a, b):
    return vincenty((a.longitude, a.latitude), (b.longitude, b.latitude)).meter


def neirest_neighbour(cells, business):
    min_dist = None
    min_neighbour = None
    for neighbour in cells.get_neighbours(cells.get_cell(business)):
        dist = distance(business, neighbour)
        if dist < min_dist or min_dist is None:
            min_dist = dist
            min_neighbour = neighbour
    return min_neighbour['id'], min_dist


def neighbours(cells, business):
    ret = []
    for neighbour in cells.get_neighbours(cells.get_cell(business)):
        ret.append({'business_id': neighbour.id,
                    'distance': distance(business, neighbour)})
    return pd.Series(ret, 'business_id')
