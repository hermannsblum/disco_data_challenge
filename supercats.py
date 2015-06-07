import pandas as pd
import numpy as np
import networkx as nx
from operator import itemgetter
import community


def add_supercats(df_in):
    """Requires df with businesses.
    Converts this to graph, then uses louvain method to find clusters

    Returns tuple of df with added super categories and mapping of supercat
    to a possible name

    super category "-1" means "uncategorized"

    Args:
        df_in (pandas.DataFrame): dataframe to be analysed
    Returns:
        (df_out, supercats):
        df_out (pandas.DataFrame): Dataframe with added column for categories
        supercats (dict): optional names for the categories in supercats
    """

    # Prepare data
    busicat = df_in['categories']

    # Find unique categories
    # all categories are lists, simply put them all together
    l = []
    for entry in busicat:
        l += entry

    # drop duplicates by converting to set
    cats = set(l)

    # Convert category entries to columns
    data = busicat.apply(lambda x: pd.Series(1, index=x))

    # Create list of data series
    mapdata = {}
    for cat in cats:
        mapdata[cat] = (data[data[cat] == 1].count())

    # Modify data to create adjacency matrix: set all values above 1 to 1
    # and set diagonal to 0
    df = pd.DataFrame(mapdata)
    np.fill_diagonal(df.values, 0)

    # Make graph from adjacency matrix
    graph = nx.from_numpy_matrix(df.values)

    # Relable nodes
    mapping = dict(zip(range(len(cats)), sorted(list(cats))))

    nx.relabel_nodes(graph, mapping, False)

    # Get Partitions with Louvain method
    part = community.best_partition(graph)

    # Structure them for info purpose
    parts_with_weights = {}
    for item in part:
        n = part[item]  # Partition number
        if n not in parts_with_weights:  # Check if list for partition exists
            parts_with_weights[n] = []

        # add node with degree in graph (for sorting) as tuples to list
        parts_with_weights[n].append((item, graph.degree()[item]))

    # Sort like you have never sorted before
    for item in parts_with_weights:
        parts_with_weights[item] = sorted(parts_with_weights[item],
                                          key=itemgetter(1),
                                          reverse=True)

    # Take first item as names (and only first part of tuple)
    supercats = (
        {key: parts_with_weights[key][0][0] for key in parts_with_weights})

    # Most convoluted function ever:
    # Make a list for every key in parts with weights (every supercategory)
    # Then turn list of tuples into list to get only names
    # Use that as an index for data
    # sum along row to get the number to see how many categories beloning to
    # the supercat are in there
    supercatframe = pd.DataFrame(
        [data[[item[0] for item in parts_with_weights[key]]].sum(axis=1)
         for key in parts_with_weights])
    # FIXME: this can be done better

    # Just use argmax to determine supercat for business: TODO: Better way?
    catmap = supercatframe.idxmax()

    # Special case: No category at all will be -1
    catmap = catmap.fillna(-1)
    supercats[-1] = "Uncategorized"

    # Add supercat to dataframe
    df_out = df_in
    df_out['super category'] = catmap

    return (df_out, supercats)
