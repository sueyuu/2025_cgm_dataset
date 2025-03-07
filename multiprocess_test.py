# %%
import numpy as np
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import logging
import os
from time_series_augmentation.utils import augmentation as aug
import concurrent.futures


# %%
# use generator to generate a new aug_arr for a entry
def custom_aug(arr, generator, label=None):
    try:
        # if not reshape, the shape will be (1440,1)
        arr = arr.reshape(-1, 1440, 1)

        if generator == "time_warp":
            aug_arr = aug.time_warp(arr, sigma=0.1)

        elif generator == "magnitude_warp":
            aug_arr = aug.magnitude_warp(arr, sigma=0.1)

        elif generator == "wdba":
            aug_arr = aug.wdba(x=arr, labels=label)

        elif generator == "rgw":
            aug_arr = aug.random_guided_warp(x=arr, labels=label)
        else:
            print("Invalid generator")
            return None

        return aug_arr
    except Exception as e:
        logging.error(f"Error processing custom_aug with generator: {generator}: {e}")
        raise


# %%
# using multithread to generate multiple aug_data parallelly from a data copy with the generators
def generate_data_parallel(data, generators, num_generation=5, label=None):

    try:

        generated_data = None

        # change data type to float for generator to use
        for generator in generators:

            if generated_data is None:

                # Create multiple aug_data of the original data in parallel
                with ThreadPoolExecutor() as executor:
                    # create num_generation futures
                    futures = [
                        executor.submit(custom_aug, data, generator, label)
                        for i in range(num_generation)
                    ]

                    # return num_generation aug_data using generator
                    results = [
                        future.result()
                        for future in concurrent.futures.as_completed(futures)
                    ]

                    # Concatenate the results
                    generated_data = np.concatenate(results, axis=0)

            else:

                # Create multiple aug_data of the once aug data in parallel
                with ThreadPoolExecutor() as executor:

                    results = list(
                        executor.map(
                            custom_aug,
                            generated_data,
                            [generator] * generated_data.shape[0],
                        )
                    )

                    # Concatenate the results
                    generated_data = np.concatenate(results, axis=0)

        return generated_data

    except Exception as e:
        logging.error(
            f"Error processing generate_data_parallel with generator: {generators}: {e}"
        )
        raise


# %%
# propcess each data numpy
def process_data_parallel(file, folder, generator):
    try:
        new_folder = folder + "_" + generator
        os.makedirs(new_folder, exist_ok=True)

        data = np.load(os.path.join(folder, file))

        data = data.astype(np.float64)

        existed = data.shape[0]

        total_needed = 90  ###total number needed may need to change

        if existed >= total_needed:
            return

        label = np.zeros((data.shape[0], 1))

        generated_data = None

        while existed < total_needed:

            num_needed = total_needed - existed
            # because both rgw and wdba will return entries the same number as input data
            num_generation = int(num_needed / data.shape[0]) + 1

            # generate new data only using original data
            aug_data = generate_data_parallel(data, [generator], num_generation, label)

            if generated_data is None:

                generated_data = aug_data

            else:
                generated_data = np.concatenate([generated_data, aug_data], axis=0)

            data = np.concatenate([data, aug_data], axis=0)

            existed += generated_data.shape[0]

        np.save(os.path.join(new_folder, file), generated_data)

    except Exception as e:
        logging.error(
            f"Error processing process_data_parallel with newfolder: generator: {folder}: {generator}: {e}"
        )
        raise


# %%
# process a folder parrallelly with a generator
def process_folder_parallel(folder, generator):

    try:

        # each datas is a datas copy for each generator
        files = [f for f in os.listdir(folder)]

        with ThreadPoolExecutor() as executor:
            executor.map(
                process_data_parallel,
                files,
                [folder] * len(files),
                [generator] * len(files),
            )
    except Exception as e:
        logging.error(
            f"Error processing process_folder_parallelly with folder: generator: {folder}: {generator}: {e}"
        )
        raise


# %%
# seperate generators to call process_folder_parallelly(for a folder)
# each generator to a process
def seperate_generator(folder, generators):
    try:

        with ProcessPoolExecutor() as executor:

            executor.map(
                process_folder_parallel, [folder] * len(generators), generators
            )
    except Exception as e:
        logging.error(f"Error processing seperate_generator: {e}")
        raise
