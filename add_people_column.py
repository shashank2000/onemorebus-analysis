import pickle
import os 
import numpy as np
import pandas as pd
from tqdm import tqdm


# open "transit_matrix.pkl"
with open("transit_matrix.pkl", "rb") as f:
    transit_matrix = pickle.load(f)

CSV_FILES = []
with open("constants.txt", "r") as f:
    # read lines one by one to populate CSV_FILES
    for line in f:
        CSV_FILES.append(line.strip())

# convert og_file to list of tuples
for index, csv_file in enumerate(CSV_FILES):
    try:
        df = pd.read_csv("heatmaps/" + csv_file)
        df['People'] = transit_matrix[index]
        # save the file
        df.to_csv("heatmaps/" + csv_file + "_new.csv")
    except:
        print("file not found: ", csv_file + "_new.csv")