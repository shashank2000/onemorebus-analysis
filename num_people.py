import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point # Point class
from pprintpp import pprint
import shapely.speedups
shapely.speedups.enable()

from collections import defaultdict
from tqdm import tqdm

BLOCK_WIDTH = 0.0038

POPULATION_STATS = {
    1: 81000,
    2: 67500,
    3: 72000,
    4: 78500,
    5: 78000,
    6: 107510,
    7: 76600,
    8: 72600,
    9: 64200,
    10: 85000,
    11: 88000
}

PERCENT_TAKING_BUS = 0.3

SF_POPULATION = sum(POPULATION_STATS.values())

df = gpd.read_file('wm84_SupeDist2022_01_pg.shp')
df = df.to_crs(epsg=4326)

NUM_BLOCKS = {}
for index, row in df.iterrows():
    polygon = row['geometry']
    supe22 = row['Supe22']
    NUM_BLOCKS[int(supe22)] = polygon.area / (BLOCK_WIDTH ** 2)

def get_district_from_point(lat, long):
    point = Point(long, lat) # little gotcha here
    for index, row in df.iterrows():
        polygon = row['geometry']
        if polygon.contains(point):
            supe22 = row['Supe22']
            return supe22
    return None

# how many people went from point A to point B
def people_on_lane(lane):
    a, b = lane
    if a == None or b == None:
        return 0
    
    a = int(a)
    b = int(b)

    # number of people in point A
    pop_a = POPULATION_STATS[a]

    # number of people in point B
    pop_b = POPULATION_STATS[b]

    # number of people taking the bus on this lane
    return PERCENT_TAKING_BUS * pop_a / NUM_BLOCKS[a] * (pop_b / SF_POPULATION)

def people_transit_matrix(coord_list):
    """
    coord_list: list of tuples of *unique* coordinates (lat, long)
    returns: 
    list of lists of people on each lane
    
    example:
    coord_list = [
        (37.7749, -122.4194), # some Marina thing
        (37.3382, -121.8863), # whatever
        (37.3382, -121.8863), # whatever
    ]
    returns: [
        [0, 10, 13],
        [7, 0, 71],
        [36, 9, 0]
    ]    
    which means 
    0 people went from 1 to 1
    10 people went from 1 to 2
    13 people went from 1 to 3
    7 people went from 2 to 1
    0 people went from 2 to 2
    71 people went from 2 to 3
    etc.
    """
    # get lanes - on a lat/long level
    lat_lng_lanes = []

    for coord in coord_list:
        for coord2 in coord_list:
            if coord != coord2:
                lat_lng_lanes.append((coord, coord2))
            else:
                lat_lng_lanes.append(((-1, -1),(-1, -1)))
                
    lanes = []

    for ((lat_1, long_1), (lat_2, long_2)) in tqdm(lat_lng_lanes):
        district1 = get_district_from_point(lat_1, long_1)
        district2 = get_district_from_point(lat_2, long_2)
        lanes.append((district1, district2))
    # get people on each lane
    people_on_lanes = [people_on_lane(lane) for lane in lanes]
    # convert people_on_lanes to a len(coord_list) x len(coord_list) matrix
    transit_matrix = []
    for i in range(len(coord_list)):
        transit_matrix.append([])
        for j in range(len(coord_list)):
            transit_matrix[i].append(people_on_lanes[i * len(coord_list) + j])
    return transit_matrix

# looping in this way to make sure we have parity with coordinates
example_coord_csv = pd.read_csv('heatmaps/37.712016_-122.38448100000006.csv')
example_coord_csv = example_coord_csv[['Latitude', 'Longitude']]

# convert example_coord_csv to list of tuples
sf_points = []
for index, row in example_coord_csv.iterrows():
    sf_points.append((row['Latitude'], row['Longitude']))
transit_matrix = people_transit_matrix(sf_points)

# pickle transit_matrix
import pickle
with open('transit_matrix.pkl', 'wb') as f:
    pickle.dump(transit_matrix, f)

