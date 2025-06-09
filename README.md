* use methods in [time_series_augmentation](https://github.com/uchidalab/time_series_augmentation.git) to augment cgm datasets

* the main running code is in healthy_intrasubject_augmentation

* it will import **multiprocess_test.py**, which leverages **time_series_augmentation.utils.augmentation.py** to do interpolation to augment dataset

* check for **def custom_aug in multiprocess_test.py** and [time_series_augmentation](https://github.com/uchidalab/time_series_augmentation.git) to see more details of the interpolation methods

* i use submodule of **time_series_augmentation**, remember to clone it with main repository

## give a pesudolabel based on sex/age/treatment/a1c grouping

## training/validation/test splitting

we first decide to split in 20/20/60 for each trials.

## smoothing time series

for removing outlier to make results more robust

we use submodule of **PyKalmanSmoothingGlucose** to smooth our time series

and because we find out that pairwise dtw distance calculation takes forever to run so we decide to downsample our training/validation set. we use only samples in original validation folder and split in 50/50 and get around 4000 samples for training/validation each.

## further process smoothed time series

because smoothed time series are too large. we downsize the original training/validation from length 8635 to 1727 for motif algorithm.

when we try running k medoid algorithm with time series with length 1727, it crushes several times so finally we have to downsize training/validation to length 157 for k medoid algorithm.

we do the same for test set too, except that each test case is not one day long data but seven day long data.

at the end, the data shape for motif and k medoid are different. with data used for k medoid are 11 times shorter than for motif.

## motif training and validation

## k medoid training and validation

## final evaluation

please reference the **evaluation model** folder, the model and testset you need are all in the folder. just run the sample code.
