from unittest import TestCase
from ydc.tools import distances, import_data


class TestDistances(TestCase):

    def setUp(self):
        super(TestDistances, self).setUp()
        self.businesses = import_data.import_businesses()[:20]

    def test_cell_creation(self):
        """Test cell creation and grid assignment"""
        grid = distances.CellCollection(1, 1)
        cell = grid.get_cell(self.businesses[1:2].squeeze())
        self.assertTrue(cell == (0, 0))
        grid2 = distances.CellCollection(100, 100)
        cell = grid2.get_cell(self.businesses[:1].squeeze())
        print(cell)
        self.assertTrue(cell != (0, 0))

    def test_neighbours(self):
        neirest = distances.neirest_neighbour(self.businesses[1:2].squeeze(),
                                              self.businesses)
