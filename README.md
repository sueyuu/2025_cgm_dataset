* use methods in [time_series_augmentation](https://github.com/uchidalab/time_series_augmentation.git) to augment cgm datasets

* the main running code is in healthy_intrasubject_augmentation

* it will import **multiprocess_test.py**, which leverages **time_series_augmentation.utils.augmentation.py** to do interpolation to augment dataset

* check for **def custom_aug in multiprocess_test.py** and [time_series_augmentation](https://github.com/uchidalab/time_series_augmentation.git) to see more details of the interpolation methods
