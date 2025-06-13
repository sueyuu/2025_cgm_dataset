here we use lynch as an example

for the csv files from other trials, the columns name and values are a little bit different but very similar to lynch

just some modification to the code and you can apply to other csv files

we first use knn to imputate all the missing values in columns

since we are not using the imputated pseudo labels for training but for stratified splitting, we do the imputation to whole group