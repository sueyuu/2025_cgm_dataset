# -*- coding: utf-8 -*-
"""cgm_processing_continuous_with_missing.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1KjvDmJA4x0HdWAPGE917xiijpkaJDItm
"""

import pandas as pd
import numpy as np
import os
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import logging
import gc


def interpolate_time_save(id_group, trial):
    id, id_df = id_group

    try:
        # sort by time
        id_df = id_df.sort_values(by=["time"])

        # Set the 'timestamp' column as the index
        new_id_df = id_df[["time", "gl"]]

        new_id_df.set_index("time", inplace=True)

        # Resample the data to 1-minute frequency and fill in with -1
        new_id_df = new_id_df.asfreq(freq="1min", fill_value=-1)

        new_id_df = new_id_df.reset_index()

        folder_path = trial + "_missing"

        # Create the folder
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, f"{id}.csv")

        new_id_df.to_csv(file_path, index=False)

        gc.collect()

    except Exception as e:
        logging.error(f"Error processing id in interpolate_time_save: {e}")
        raise


# for each df of different trials(for each item in df_dictionary), group by id and then time
def chunk_id(trial, df):

    try:

        df = df[["id", "time", "gl"]]

        # change dtypes of time column to timestamp
        df["time"] = pd.to_datetime(df["time"])

        # sort by id and time
        df = df.sort_values(by=["id", "time"])

        # round timestamp in 'time' column to minute
        df["time"] = df["time"].dt.round("1min")

        # Remove redundant rows based on 'id' and 'time', keeping the first occurrence
        df = df.drop_duplicates(subset=["id", "time"], keep="first")

        # Group by id
        id_group = df.groupby("id")

        # Process each id_group in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            executor.map(interpolate_time_save, id_group, [trial] * len(id_group))

    except Exception as e:
        logging.error(f"Error processing trial in chunk_id: {trial}: {e}")
        raise
