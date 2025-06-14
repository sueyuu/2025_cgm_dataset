## requirement

first create and env with python 3.9.21 and use conda to install the following
pandas 2.2.3
numpy 1.26.3
scipy 1.13.1
tslearn 0.6.3
sktime 0.36.0
seaborn 0.13.2
matplotlib 3.9.4

and use pip to install
torch 2.6.0 (you need to install with command in official website)
torchdrift 0.1.0

## clone note

we use submodule in our project, remember to clone in recursive

## get demographic, hba1c and cgm data from a single trial

use **get_features** folder, first read folder's readme

contributor: 
[@sueyuu](https://github.com/sueyuu)

##create_cgm_folder

create folders containing processed cgm data for each trial

use **create_cgm_folder**, first read folders'readme

contributor: 
[@sueyuu](https://github.com/sueyuu)

#synthessize healthy data

use **healthy_synthesis** folder, first read folder's readme

use methods in [time_series_augmentation](https://github.com/uchidalab/time_series_augmentation.git) to synthesize cgm datasets

contributor: 
[@sueyuu](https://github.com/sueyuu)

## generate sex, age, treatment, a1c group columns

use **discretize** folder, first read folder's readme

contributor:
[@sueyuu](https://github.com/sueyuu)
[Young](mailto:Sydg0705@icloud.com)
[Shem](mailto:shemlawalata@gmail.com)
[@weixiang0470](https://github.com/weixiang0470)
[@RowDM](https://github.com/RowDM)
[Conrad](mailto:conrad15jones@gmail.com)

## filter out subjects that do not have data long enough for evaluation

use **filter_by_len folder**, first read folder's readme

contributor:
[Young](mailto:Sydg0705@icloud.com)
[@RowDM](https://github.com/RowDM)
[Shem](mailto:shemlawalata@gmail.com)

## imputate missing a1c value, we use mean glucose in cgm to estimlate a1c values

use **a1c_imputation** folder, first read folder's readme

we use mean glucose of all the cgm from a certain subject to estimate missing mean hba1c

contributor:
[Shem](mailto:shemlawalata@gmail.com)

## give a pesudolabel based on sex/age/treatment/a1c grouping

use **imputation** folder, first read folder's readme

we generate a pseudolabel here because we later will use pseudolabel to do stratified splitting and also use pseudolabel for test set evaluation

for missing value, we use knnimputator to impute

contributor:
[@sueyuu](https://github.com/sueyuu)

## training/validation/test splitting

use **splitting folder**, first read folder's readme

we put our default code with splitting ratio 20/20/60 here.

contributor:
[@RowDM](https://github.com/RowDM)

## smoothing time series

use **smoothing** folder, first read folder's readme

for removing outlier to make results more robust

we use submodule of [PyKalmanSmoothingGlucose](https://github.com/miriamkw/PyKalmanSmoothingGlucose.git) to smooth our time series

and because we find out that pairwise dtw distance calculation takes forever to run so we decide to downsample our training/validation set. we use only samples in original validation folder and split in 50/50 and get around 4000 samples for training/validation each.

because smoothed time series are too large. we downsize the original training/validation from length 8635 to 1727 for motif algorithm.

when we try running k medoid algorithm with time series with length 1727, it crushes several times so finally we have to downsize training/validation to length 157 for k medoid algorithm.

we do the same for test set too, except that each test case is not one day long data but seven day long data.

at the end, the data shape for motif and k medoid are different. with data used for k medoid are 11 times shorter than for motif.

contributor:
[Conrad](mailto:conrad15jones@gmail.com)

## motif training and validation

use **motifs** folder, first read folder's readme

contributor:
[@weixiang0470](https://github.com/weixiang0470)

## k medoid training and validation

use **k_medoid** folder, first read folder's readme

contributor:
[@sueyuu](https://github.com/sueyuu)

## final evaluation

use **evaluation model** folder, the model and testset you need are all in the folder.

first unzip test folders and read readme in subfolder to do all the steps and run evaluation_v2.ipynb.

contributor:
[@sueyuu](https://github.com/sueyuu)
[Young](mailto:Sydg0705@icloud.com)
[Shem](mailto:shemlawalata@gmail.com)
[@weixiang0470](https://github.com/weixiang0470)
[@RowDM](https://github.com/RowDM)
[Conrad](mailto:conrad15jones@gmail.com)