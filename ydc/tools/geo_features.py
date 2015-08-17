from ydc.tools.distances import make_cell_collection
from ydc.tools.import_data import import_businesses
from ydc.tools.supercats import add_supercats
from ydc.tools.geografik import region, region_cells, dict_to_kml, \
    categories_kml, cat_color, resolution_to_meters
from ydc.features.stars import stars_stats
import numpy as np
import pandas as pd
from copy import deepcopy
from os import path

from simplekml import Kml, Style
from colorsys import hsv_to_rgb


def delta_stars(resolution, city, new_cache=False):
    def norm_stars_color(delta_stars):
        norm_value = (1 - delta_stars ** 2)
        return '{0:02x}{1:02x}{1:02x}{1:02x}'.format(255, int(norm_value * 255))

    (businesses, box, combo) = add_supercats(import_businesses(), new_cache=new_cache)
    cells = make_cell_collection(resolution, businesses, new_cache=new_cache)
    (norm_stars_dict, region_businesses) = region_cells(businesses, cells, city, 5)

    # make dataframe with mean over sub-categories
    cat_means = {}
    for subcat in combo:
        cat_means[str(subcat)] = businesses[
            businesses['category'] == subcat]['real_stars'].mean()
    cat_means = pd.Series(cat_means, name='category_mean_stars')
    region_businesses['category_str'] = region_businesses['category'].apply(str)
    region_businesses = region_businesses.join(cat_means, on='category_str')
    region_businesses['delta_stars'] = region_businesses['real_stars'] \
        - region_businesses['category_mean_stars']
    
    #normalize from 0 to 1
    region_businesses['delta_stars'] = (region_businesses['delta_stars'] 
        - region_businesses['delta_stars'].min()) / \
        (region_businesses['delta_stars'].max() 
         - region_businesses['delta_stars'].min())

    for x, row in norm_stars_dict.items():
        for y, cell in row.items():
            norm_stars_dict[x][y] = np.mean(
                region_businesses.loc[cell]['delta_stars'])

    # convert resolution into m
    # pick random cell
    rand_cell = cells.get_cell(region_businesses.iloc[0])
    res_meters = resolution_to_meters(rand_cell, cells.get_borders())

    kml = Kml()
    kml = dict_to_kml(kml, cells.get_borders(), norm_stars_dict, norm_stars_color)
    kml_path = path.join('kml_files',
                         '{}_norm_stars_density_{}.kml'.format(res_meters, city))
    kml.save(kml_path)


def review_counts(resolution, city, new_cache=False):
    def review_count_color(review_count, maximum=0):
        norm_value = (1 - ((review_count) / (maximum))) 
        return '{0:02x}{1:02x}{1:02x}{1:02x}'.format(255, int(norm_value * 255))

    (businesses, box, combo) = add_supercats(import_businesses(), new_cache=new_cache)
    cells = make_cell_collection(resolution, businesses, new_cache=new_cache)
    (region_dict, region_businesses) = region_cells(businesses, cells, city, 5)

    review_count_dict = {}
    for x, row in region_dict.items():
        review_count_dict[x] = {}
        for y, cell in row.items():
            mean = np.mean(region_businesses.loc[cell]['review_count_last_year'])
            if mean > 0:
                review_count_dict[x][y] = mean

    # normalize data
    values = [item for row in review_count_dict.values() for item in row.values() \
        if item is not np.nan]
    maximum = np.max(values)

    # convert resolution into m
    # pick random cell
    rand_cell = cells.get_cell(region_businesses.iloc[0])
    res_meters = resolution_to_meters(rand_cell, cells.get_borders())

    # save KML
    kml = Kml()
    kml = dict_to_kml(kml, cells.get_borders(), review_count_dict, review_count_color,
                      maximum=maximum)
    kml_path = path.join('kml_files',
                         '{}_review_count_density_{}.kml'.format(res_meters, city))
    kml.save(kml_path)


def cat_density(resolution, city, new_cache=False):
    def cat_dens_color(cell, maximum=0):
        rgb_tuple = hsv_to_rgb(0, 0, (cell / maximum) ** 2)
        alpha = 1
        """ convert an (R, G, B) tuple to #AARRGGBB """
        rgb_tuple = (alpha*255, rgb_tuple[0]*255, rgb_tuple[1]*255, rgb_tuple[2]*255)
        hexcolor = '%02x%02x%02x%02x' % rgb_tuple
        return hexcolor

    (businesses, box, combo) = add_supercats(import_businesses(), new_cache=new_cache)
    cells = make_cell_collection(resolution, businesses, new_cache=new_cache)
    (region_dict, region_businesses) = region_cells(businesses, cells, city, 5)

    print('find the cell-coordinates', end='\r')
    region_businesses['cell_coord'] = region_businesses.apply(lambda row: cells.get_cell(row), axis=1)
    grouped = region_businesses.groupby('cell_coord')

    print('creating folders', end='\r')
    kml = Kml()
    # Create folder for every category and save them in dictionary
    folders = {key: kml.newfolder(name=box[key]['name']) for key in box}
    # More subfolders for subcats
    subfolders = {}
    for superkey in folders:
        subcats = box[superkey]['sub_categories']
        subfolders[superkey] = {key: folders[superkey].newfolder(name=subcats[key]['name']) for key in subcats}

    for cat in combo:
        print('analyzing {}'.format(combo[cat]), end='\r')
        in_cat = region_businesses['category'] == cat
        cat_dens_dict = {}
        for x, row in region_dict.items():
            cat_dens_dict[x] = {}
            for y, cell in row.items():
                count = grouped.get_group((x, y))[in_cat]['business_id'].count()
                if count > 0:
                    cat_dens_dict[x][y] = count
        values = [item for row in cat_dens_dict.values() for item in row.values()\
            if item is not np.nan]
        if len(values) > 0:
            maximum = np.max(values)
            subfolders[cat[0]][cat[1]] = dict_to_kml(subfolders[cat[0]][cat[1]], cells.get_borders(),
                                                     cat_dens_dict, cat_dens_color, maximum=maximum)

    # convert resolution into m
    rand_cell = cells.get_cell(region_businesses.iloc[0])
    res_meters = resolution_to_meters(rand_cell, cells.get_borders())

    kml_path = path.join('kml_files',
                         '{}_category_density_{}.kml'.format(res_meters, city))
    kml.save(kml_path)


def supercat_density(resolution, city, new_cache=False):
    def cat_dens_color(cell, maximum=0):
        norm_value = 1 - ((cell) / (maximum))
        return '{0:02x}{1:02x}{1:02x}{1:02x}'.format(255, int(norm_value*255))

    (businesses, box, combo) = add_supercats(import_businesses(), new_cache=new_cache)
    cells = make_cell_collection(resolution, businesses, new_cache=new_cache)
    (region_dict, region_businesses) = region_cells(businesses, cells, city, 5)

    # add cell coordinate to dataframe, group businesses by cells
    region_businesses['cell_coord'] = region_businesses.apply(lambda row: cells.get_cell(row), axis=1)
    grouped = region_businesses.groupby('cell_coord')

    kml = Kml()
    # Create folder for every category and save them in dictionary
    folders = {key: kml.newfolder(name=box[key]['name']) for key in box}

    for cat in box:
        print('analyzing {}'.format(box[cat]['name']), end='')
        cat_dens_dict = {}
        in_cat = region_businesses['super_category'] == cat
        for x in region_dict:
            if x not in cat_dens_dict:
                cat_dens_dict[x] = {}
            for y in region_dict[x]:
                # count the number of businesses of cat in this cell
                count = grouped.get_group((x, y))[in_cat]['business_id'].count()
                # only add cell if there exist such businesses
                if count > 0:
                    cat_dens_dict[x][y] = grouped.get_group((x, y))[in_cat]['business_id'].count()
        values = [item for row in cat_dens_dict.values() for item in row.values()]
        maximum = np.max(values)
        print(', maximum: {}'.format(maximum))
        folders[cat] = dict_to_kml(folders[cat], cells.get_borders(),
                                                 cat_dens_dict, cat_dens_color, maximum=maximum)

    # convert resolution into m
    rand_cell = cells.get_cell(region_businesses.iloc[0])
    res_meters = resolution_to_meters(rand_cell, cells.get_borders())

    kml_path = path.join('kml_files', '{}_super_cat_dens_{}.kml'.format(
        res_meters, city))
    kml.save(kml_path)
    print('saved')


def cat_distribution(resolution, city):
    def cat_to_color(cat, box=None):
        return '{0:02x}{1}'.format(180, cat_color((cat, 0), box))

    (businesses, box, combo) = add_supercats(import_businesses())
    cells = make_cell_collection(resolution, businesses)
    (region_dict, region_businesses) = region_cells(businesses, cells, city, 5)

    # find general distribution of categories
    std_group = region_businesses.groupby('super_category')['business_id'].count()
    std_group = std_group / std_group.max()

    # add cell coordinate to dataframe, group businesses by cells
    region_businesses['cell_coord'] = region_businesses.apply(lambda row: cells.get_cell(row), axis=1)
    grouped = region_businesses.groupby('cell_coord')

    distribution_dict = {}
    for x, row in region_dict.items():
        distribution_dict[x] = {}
        for y in row:
            max_cat = None
            max_count = 0
            in_cell = grouped.get_group((x, y))
            max_cat = in_cell.groupby('super_category')['business_id'].count()
            max_cat = max_cat / std_group
            max_cat = max_cat.idxmax()
            # don't show uncategorized
            if max_cat != -1:
                distribution_dict[x][y] = max_cat

    # convert resolution into m
    rand_cell = cells.get_cell(region_businesses.iloc[0])
    res_meters = resolution_to_meters(rand_cell, cells.get_borders())

    kml = Kml()
    kml = dict_to_kml(kml, cells.get_borders(), distribution_dict, cat_to_color,
                      box=box)
    kml_path = path.join('kml_files',
                         '{}_cat_distribution_{}.kml'.format(res_meters, city))
    kml.save(kml_path)

    # save legend in html
    html_path = path.join('kml_files',
                         '{}_cat_distribution_{}.html'.format(res_meters, city))
    legend = "<html><head></head><body>"
    for cat in box:
        # we don't show uncategorized, so we need no legend for this
        if cat == -1:
            continue
        legend += ("&nbsp;{0}<div style='height: 15px; width: 100px; float: left; "
                   "background-color: #{1};'></div><br>")\
            .format(box[cat]['name'], cat_color((cat, 0), box))
    legend += "</body></html>"
    
    html = open(html_path, 'w')
    html.write(legend)
    html.close()


def businesses_markers(city):
    (businesses, box, combo) = add_supercats(import_businesses(), new_cache=new_cache)
    cells = make_cell_collection(resolution, businesses, new_cache=new_cache)
    (region_dict, region_businesses) = region_cells(businesses, cells, city, 5)

    # define styles
    #Create color for every category and also save them in dict
    styles = {}
    for superkey in box:
        subcats = box[superkey]['sub_categories']
        # Create dict of dicts with entries for every subcategory
        styles[superkey] = {key: Style() for key in subcats}
        for key in subcats:
            styles[superkey][key].labelstyle.scale = 0
            hue = superkey/(len(box.keys()) - 1)  # Around the circle
            sat = 0.5 + key/(2 * len(subcats.keys()))  # Avoid the middle so not everything gets white
            styles[superkey][key].iconstyle.icon.href = (
                'http://thydzik.com/thydzikGoogleMap/markerlink.php?color=%s' % cat_color((superkey, key), box)
            )
    #Special case for uncategories (those are -1 and will be black)
    styles[-1] = {-1: Style()}
    styles[-1][-1].labelstyle.scale = 0
    styles[-1][-1].iconstyle.icon.href = 'http://thydzik.com/thydzikGoogleMap/markerlink.php?color=000000'

    kml = Kml()
    kml = categories_kml(kml, styles, region_dict, businesses, box)
    kml_path = path.join('kml_files',
                         'businesses_markers_{}.kml'.format(city))
    kml.save(kml_path)


def businesses_point(city, new_cache=False):
    (businesses, box, combo) = add_supercats(import_businesses(), new_cache=new_cache)
    cells = make_cell_collection(15, businesses, new_cache=new_cache)
    (region_dict, region_businesses) = region_cells(businesses, cells, city, 5)

    # define styles
    #Create color for every category and also save them in dict
    styles = {}
    for superkey in box:
        subcats = box[superkey]['sub_categories']
        # Create dict of dicts with entries for every subcategory
        styles[superkey] = {key: Style() for key in subcats}
        for key in subcats:
            styles[superkey][key].labelstyle.scale = 0
            hue = superkey/(len(box.keys()) - 1)  # Around the circle
            sat = 0.5 + key/(2 * len(subcats.keys()))  # Avoid the middle so not everything gets white
            styles[superkey][key].linestyle.color = '{0:02x}{1}'.format(
                255, cat_color((superkey, key), box))
            styles[superkey][key].linestyle.gxoutercolor = '{0:02x}{1}'.format(
                255, cat_color((superkey, key), box))
            styles[superkey][key].linestyle.width = 2
            styles[superkey][key].linestyle.gxouterwidth = 2
            styles[superkey][key].linestyle.gxphysicalwidth = 2
            styles[superkey][key].iconstyle.scale = 0
    #Special case for uncategories (those are -1 and will be black)
    styles[-1] = {-1: Style()}
    styles[-1][-1].labelstyle.scale = 0
    styles[-1][-1].linestyle.color = '00000000'
    styles[-1][-1].linestyle.width = 2
    styles[-1][-1].iconstyle.scale = 0

    kml = Kml()
    kml = categories_kml(kml, styles, region_dict, businesses, box)
    kml_path = path.join('kml_files',
                         'businesses_points_{}.kml'.format(city))
    kml.save(kml_path)
