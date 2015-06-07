from unittest import TestCase
from ydc.tools import distances, import_data
# from ydc.tools import distances_memcells
# import time


class TestDistances(TestCase):

    def setUp(self):
        super(TestDistances, self).setUp()
        self.businesses = import_data.import_businesses()[:20]

    def test_neighbours(self):
        # create cell collection
        cells = distances.CellCollection(15, self.businesses)

        neirest = cells.get_neighbours(self.businesses[1:2].squeeze(), num=1)
        neirest = neirest[0]
        self.assertTrue('distance' in neirest.keys())

        small_region = cells.get_neighbours(self.businesses[1:2].squeeze(),
                                            num=10)
        indizes = []
        for item in small_region:
            indizes.append(item['index'])
        self.assertTrue(neirest['index'] in indizes)

        # cells = distances_memcells.CellCollection(80000, 40000,
        #                                           self.businesses)
        # cells.get_neighbours(self.businesses[1:2].squeeze(), self.businesses)

    def test_performance(self):

        """
        print("Testing the Filterung")
        print("filter")
        start = time.clock()
        for i in range(100):
            left = self.businesses[self.businesses.longitude < 1.2]
            right = self.businesses[self.businesses.longitude >= 1.2]
        end = time.clock()
        print((end-start)/100)

        print("notin")
        start = time.clock()
        for i in range(100):
            left = self.businesses[self.businesses.longitude < 1.2]
            right = self.businesses[~self.businesses.isin(left)]
        end = time.clock()
        print((end-start)/100)

        print("apply")
        start = time.clock()
        for i in range(100):
            left = self.businesses.apply(lambda row: row.longitude < 1.2,
                                         axis=1)
            one = self.businesses[left == 1]
            two = self.businesses[left == 0]
        end = time.clock()
        print((end-start)/100)

        print("query")
        start = time.clock()
        for i in range(100):
            left = self.businesses.query("longitude < {}".format(1.2))
            right = self.businesses.query("longitude >= {}".format(1.2))
        end = time.clock()
        print((end-start)/100)

        self.assertTrue(False)
        """
        """
        print("Creating CellCollection")
        start = time.clock()
        cells = distances.CellCollection(15, self.businesses)
        end = time.clock()
        print((end - start))

        print("Find Neighbours in CellCollection")
        start = time.clock()
        for i in range(10):
            cells.get_neighbours(self.businesses[1:2].squeeze())
        end = time.clock()
        print((end - start) / 10)

        print("Find Neighbours in whole DataFrame")
        start = time.clock()
        for i in range(10):
            distances.get_neighbours(self.businesses[1:2].squeeze(),
                                     self.businesses)
        end = time.clock()
        print((end - start) / 10)

        self.assertTrue(False)
        """
"""

    def test_recursive_cells(self):

        Test the recursive implementation
        start = time.clock()
        cells = distances_memcells.Cell(-180, 180, -90, 90, 5)
        for idx, business in self.businesses.iterrows():
            cells.append(business.to_dict())
        end = time.clock()
        print(end-start)

        start = time.clock()
        cells = distances_memcells.CellCollection(15, self.businesses)
        end = time.clock()
        print((end-start))
        self.assertTrue(False)

"""
