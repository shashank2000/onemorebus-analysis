import pickle
import os 
import numpy as np
import pandas as pd
from tqdm import tqdm
from argparse import ArgumentParser

# open "transit_matrix.pkl"
with open("transit_matrix.pkl", "rb") as f:
    transit_matrix = pickle.load(f)

CSV_FILES = []
with open("constants.txt", "r") as f:
    # read lines one by one to populate CSV_FILES
    for line in f:
        CSV_FILES.append(line.strip())

def add_people_column(heatmap_dir):
    # convert og_file to list of tuples
    for index, csv_file in enumerate(CSV_FILES):
        try:
            file_name = os.path.join(heatmap_dir, csv_file)
            df = pd.read_csv(file_name)
            df['People'] = transit_matrix[index]
            # save the file
            df.to_csv(file_name)
        except:
            print("file not found: ", file_name)

if __name__ == "__main__":
    argparse = ArgumentParser()
    argparse.add_argument("--heatmap_dir", type=str, default="heatmaps")
    args = argparse.parse_args()
    heatmap_dir = args.heatmap_dir
    add_people_column(heatmap_dir)