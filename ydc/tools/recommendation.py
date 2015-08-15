def recommended_cells(resolution, city, new_cache=False):
    def count_color(count, maximum=0):
        norm_value = (1 - (count / maximum) ** 2) 
        return '{0:02x}{1:02x}{1:02x}{1:02x}'.format(255, int(norm_value * 255))

    (businesses, box, combo) = add_supercats(import_businesses(), new_cache=new_cache)
    cells = make_cell_collection(resolution, businesses, new_cache=new_cache)
    (region_dict, region_businesses) = region_cells(businesses, cells, city, 5)
    # region_dict is a cell_dict including only cells of the region
    # region_businesses is businesses filtered for the region
    # so just filter the region_businesses dataframe ang give if back :)



    # Space for you


    # please remove the following line
    recommended_businesses = region_businesses
    
    # we now group the recommended businesses by cells
    recommended_businesses['cell_coord'] = recommended_businesses.apply(lambda row: cells.get_cell(row), axis=1)
    grouped = recommended_businesses.groupby('cell_coord')
    recommend_dict = {}
    for x, row in region_dict.items():
        recommend_dict[x] = {}
        for y in row:
            count = grouped.get_group((x, y))['business_id'].count()
            # only add cells where we would recommend at least one location
            if count > 0:
                recommend_dict[x][y] = count

    # normalize data
    values = [item for row in review_count_dict.values() for item in row.values() \
        if item is not np.nan]
    maximum = np.max(values)

    # convert resolution into m
    # pick random cell
    rand_cell = cells.get_cell(recommended_businesses.iloc[0])
    res_meters = resolution_to_meters(rand_cell, cells.get_borders())

    # save KML
    kml = Kml()
    # this creates the actual kml from the dict
    kml = dict_to_kml(kml, cells.get_borders(), recommend_dict, count_color,
                      maximum=maximum)
    kml_path = path.join('kml_files',
                         '{}_recommendations_{}.kml'.format(res_meters, city))
    kml.save(kml_path)
