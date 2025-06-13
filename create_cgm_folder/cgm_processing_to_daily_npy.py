# %%
import pandas as pd
import numpy as np
import os
import zipfile
from IPython.display import display
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import logging
import gc

# %% [markdown]
# #each date_df is a continuous data from a patient, we do interpolation and return the dataframe


# %%
# for each date_df do interpolation and return interpolated date_df
def time_interpolation_of_day(date_df):
    try:

        if date_df.empty:
            return None

        # Set the 'timestamp' column as the index
        date_df.set_index("time", inplace=True)

        # Resample the data to 1-minute frequency and interpolate missing values
        date_df = date_df.resample("min").interpolate()

        # need to reset index or cannot filter
        date_df = date_df.reset_index()

        # check nan in gl column
        if date_df["gl"].isna().sum() > 0:
            # remove rows with nan value
            date_df = date_df.dropna(subset=["gl"])

        date_df["gl"] = date_df["gl"].astype(int)

        # Find the entry with timestamp at midnight
        midnight = date_df[date_df["time"].dt.time == pd.Timestamp("00:00").time()]

        # make sure at least one day data available
        if len(midnight) < 2:
            return None

        # Find the first midnight entry
        first_midnight_time = midnight.iloc[0].at["time"]

        # Find the last midnight entry
        last_midnight_time = midnight.iloc[-1].at["time"]

        # Filter the DataFrame to keep only the between first and last midnight
        date_df = date_df[
            (date_df["time"] >= first_midnight_time)
            & (date_df["time"] < last_midnight_time)
        ]

        # --- Filter out the remainder rows from the beginning ---
        # the following code are just left for double check
        total_rows = len(date_df)

        remainder = total_rows % 1440

        if remainder != 0:
            start_index = remainder
            date_df = date_df.iloc[start_index:]  # Keep rows from start_index to end
            print(f"Removed {remainder} rows")

        # return date_df start from 00:00 and end at 11:59 with 1 min interpolation
        return date_df

    except Exception as e:
        logging.error(f"Error processing date_df: {e}")
        raise


# %% [markdown]
# #for each id(patient), chunk dataframe if there is any time difference for over 3 hours, and then call function to interpolate. After interpolation, concat possible continuous data together(with <= 1 day diff)


# %%
def chunk_by_time(id_group):
    id, id_df = id_group

    try:
        # sort by time
        id_df = id_df.sort_values(by=["time"])

        # Reset index
        id_df = id_df.reset_index(drop=True)

        # Create a column with date diff from the previous entry
        id_df["diff_time"] = id_df["time"].diff()

        # Filter out rows where 'diff_time' is greater than 3 hours
        split_indices = id_df.index[
            id_df["diff_time"] >= pd.Timedelta(hours=3)
        ].tolist()

        # Add the first and last index to the split points
        # it is ok if the last one and the second last one are both id_df.index[-1] because we will remove empty df
        split_indices = [0] + split_indices + [id_df.index[-1]]

        # Split the DataFrame into chunks based on the split points and make deep copies
        chunks = [
            id_df.iloc[split_indices[i] : split_indices[i + 1]]
            .copy(deep=True)
            .reset_index(drop=True)
            for i in range(len(split_indices) - 1)
        ]

        # do interpolation to all chunks in parallel
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(time_interpolation_of_day, chunks))

        # Remove None results
        results = [e for e in results if e is not None]

        # if a chunk's tail and next chunk's head timestamp is within 1 days, concat
        i = 0
        while i < len(results) - 1:
            prev_tail_time = results[i].iloc[-1].at["time"]
            next_head_time = results[i + 1].iloc[0].at["time"]
            if (next_head_time - prev_tail_time).days <= 1:
                results[i] = pd.concat([results[i], results[i + 1]])
                # sort by time
                results[i] = results[i].sort_values(by=["time"])
                # reset index
                results[i].reset_index(drop=True, inplace=True)
                results.pop(i + 1)
            i += 1

        gc.collect()

        return results

    except Exception as e:
        logging.error(f"Error processing id in chunk_by_time: {id}: {e}")
        raise


# %% [markdown]
# #save each chunk to npy

# %%
from datetime import time


# save each chunk of the result
def save_chunk_in_result(i, chunk, trial):
    try:
        if chunk is None:
            return
        if chunk.empty:
            return

        # get first index
        first_idx = chunk.index[0]

        # get id from first index
        id = chunk.at[first_idx, "id"]

        # round time column to date and save unique values(date)
        chunk_date = chunk["time"].dt.date.unique()

        gl_array = chunk["gl"].to_numpy()

        gl_array = gl_array.reshape(-1, 1440)

        gl_array = np.expand_dims(
            gl_array, axis=-1
        )  # shape is (days, 1440(timestamp), 1(glucose)) for each chunk

        folder_path = trial

        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, f"{id}_{i}.npy")

        np.save(file_path, gl_array)

        time_folder_path = os.path.join(folder_path + "_time")

        os.makedirs(time_folder_path, exist_ok=True)

        time_file_path = os.path.join(time_folder_path, f"{id}_{i}_time.npy")

        np.save(time_file_path, chunk_date)

        return
    except Exception as e:
        logging.error(f"Error processing trial in save_chunk_in_result: {trial}: {e}")
        raise


# %%
# each result is a list of chunks for each id
def save_result_for_id(result, trial):
    try:

        if not result:
            return

        trials = [trial] * len(result)

        # Enumerate over the zipped lists
        enumerated_zipped_lists = enumerate(zip(result, trials))

        # Save each chunk in result in parallel
        with ThreadPoolExecutor() as executor:
            executor.map(
                lambda args: save_chunk_in_result(args[0], *args[1]),
                enumerated_zipped_lists,
            )

    except Exception as e:
        logging.error(f"Error processing trial save_result_for_id: {trial}: {e}")
        raise


# %% [markdown]
# # for each trial, group dataframe by id and then apply further function


# %%
# for each df of different trials(for each item in df_dictionary), group by id and then time
def chunk_id_and_time(trial, df, healthy=False):

    try:

        df = df[["id", "time", "gl"]]

        # change dtypes of time column to timestamp
        df["time"] = pd.to_datetime(df["time"])

        # sort by id and time
        df = df.sort_values(by=["time", "id"])

        # round timestamp in 'time' column to minute
        df["time"] = df["time"].dt.round("1min")

        # Remove redundant rows based on 'id' and 'time', keeping the first occurrence
        df = df.drop_duplicates(subset=["id", "time"], keep="first")

        # Group by id
        id_group = df.groupby("id")

        # Process each id_group in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(chunk_by_time, id_group))

        if not results:
            return

        # remove result which is empty list
        results = [result for result in results if result]

        """
    although there is large intervals between each chunk in results
    the pattern would not change much in healthy subjects
    it is ok to concatenate them together
    and generate numpy array with shape(days, 1440(timestamp))
    """
        """
    but in t1 patient, different chunks should be seperated
    """
        # if healthy, concatenate df in each result together
        if healthy:

            results = [[pd.concat(result).reset_index(drop=True)] for result in results]

        with ThreadPoolExecutor() as executor:

            executor.map(save_result_for_id, results, [trial] * len(results))

    except Exception as e:
        logging.error(f"Error processing trial in chunk_id_and_time: {trial}: {e}")
        raise
