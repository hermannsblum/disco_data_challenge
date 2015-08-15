from ydc.tools.distances import CellCollection
from ydc.features.stars import stars_stats
from simplekml import Kml, Style
from colorsys import hsv_to_rgb
from ydc.tools.cache import cache_result
from geopy.distance import vincenty
from os import path
from numpy import nan

def region(businesses, cells, city, radius):
    random_choice = businesses[businesses['city'] == city][:1].squeeze()
    region_indices = [item['index'] for item in 
        cells.get_region(random_choice, radius)]
    return list(set(
        businesses.iloc[region_indices]['city'].tolist()))


def region_cells(businesses, cells, city, radius):
    region_filter = region(businesses, cells, city, radius)
    region_bizs = businesses[businesses['city'].isin(region_filter)]
    region_cell_coords = []
    for idx, biz in region_bizs.iterrows():
        region_cell_coords.append(cells.get_cell(biz))
    region_cell_coords = set(region_cell_coords)
    cell_dict = cells.to_dict()
    ret = {}
    for coord in region_cell_coords:
        if coord[0] not in ret:
            ret[coord[0]] = {}
        ret[coord[0]][coord[1]] = [i['index'] for i in cell_dict[coord[0]][coord[1]]]
    return ret, region_bizs


def dict_to_kml(kml, borders, cell_dict, color_mapper, **kwargs):
    def make_polygon(folder, name, lowerleft, upperright, color):
        pol = folder.newpolygon(name=name)
        pol.extrude = 1
        coords = [lowerleft,
                  (lowerleft[0], upperright[1]),
                  upperright,
                  (upperright[0], lowerleft[1]),
                  lowerleft]
        pol.outerboundaryis = coords
        pol.style.polystyle.color = color

    longitudes = borders[0]
    latitudes = borders[1]
    for x, row in cell_dict.items():
        for y, cell in row.items():
            if cell is not nan:
                make_polygon(kml, 'Cell-{}-{}'.format(x, y),
                             (longitudes[x], latitudes[y]),
                             (longitudes[x+1], latitudes[y+1]),
                             color_mapper(cell, **kwargs))
    return kml


def cat_color(category, box):
    if category[0] == 0: 
        return '000000'
    hue = category[0]/(len(box.keys()) - 1)  # Around the circle
    # Avoid the middle so not everything gets white
    saturation = 0.5 + category[1]/(2 * len(box[category[0]]['sub_categories'].keys()))
    rgb_tuple = hsv_to_rgb(hue, saturation,1)
    """ convert an (R, G, B) tuple to #RRGGBBff """
    rgb_tuple = (rgb_tuple[0]*255, rgb_tuple[1]*255, rgb_tuple[2]*255)
    hexcolor = '%02x%02x%02x' % rgb_tuple
    return hexcolor


def categories_kml(folder, styles, cell_dict, businesses, box):

    # Create folder for every category and save them in dictionary
    folders = {key: folder.newfolder(name=box[key]['name']) for key in box}
    # More subfolders for subcats
    subfolders = {}
    for superkey in folders:
        subcats = box[superkey]['sub_categories']
        subfolders[superkey] = {key: folders[superkey].newfolder(name=subcats[key]['name']) for key in subcats}

    # List all businesses in the cell_dict
    index_list = [item for row in cell_dict.values() for cell in row.values() for item in cell]

    # insert businesses into kml
    for idx, item in businesses.loc[index_list].iterrows():
        pnt = subfolders[item['super_category']][item['sub_category']].newpoint(
            name=item['name'], 
            coords=[(item['longitude'],item['latitude'])])
        pnt.style = styles[item['super_category']][item['sub_category']]


"""
def categories_squares(folder, styles, cell_dict, businesses, box):
    def make_square(folder, name, point, color):
        pol = folder.newpolygon(name=name)
        pol.extrude = 1
        coords = [point,
                  (point[0], point[1] + 0.00005),
                  (point[0] + 0.00005, point[1] + 0.00005),
                  (point[0] + 0.00005, point[1]),
                  point]
        pol.outerboundaryis = coords
        pol.style.polystyle.color = color

    # Create folder for every category and save them in dictionary
    folders = {key: folder.newfolder(name=box[key]['name']) for key in box}
    # More subfolders for subcats
    subfolders = {}
    for superkey in folders:
        subcats = box[superkey]['sub_categories']
        subfolders[superkey] = {key: folders[superkey].newfolder(name=subcats[key]['name']) for key in subcats}

    # List all businesses in the cell_dict
    index_list = [item for row in cell_dict.values() for cell in row.values() for item in cell]

    # insert businesses into kml
    for idx, item in businesses.loc[index_list].iterrows():
        make_square(subfolders[item['super_category']][item['sub_category']],
                    name=item['name'],
                    point=(item['longitude'],item['latitude']),
                    color=asd)
        pnt = newpoint(
            coords=[(item['longitude'],item['latitude'])])
        pnt.style = styles[item['super_category']][item['sub_category']]

    return folder

"""
def resolution_to_meters(cell, borders):
    longitudes = borders[0]
    latitudes = borders[1]
    km_dist = vincenty((longitudes[cell[0]], latitudes[cell[1]]),
                       (longitudes[cell[0]], latitudes[cell[1] + 1])).km
    return int(km_dist * 1000)

