from unittest import TestCase
from ydc.tools import distances, import_data


class TestDistances(TestCase):

    def setUp(self):
        super(TestDistances, self).setUp()
        self.businesses = import_data.import_businesses()[:20]

    def test_neighbours(self):
        neirest = distances.neirest_neighbour(self.businesses[1:2].squeeze(),
                                              self.businesses)

        small_region = distances.get_neighbours(self.businesses[1:2].squeeze(),
                                                self.businesses)
        self.assertTrue(neirest.business_id in small_region['business_id'].tolist())
