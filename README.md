[![Build Status](https://ahmad88me.semaphoreci.com/badges/tada-qq/branches/master.svg)](https://ahmad88me.semaphoreci.com/projects/tada-qq)
[![codecov](https://codecov.io/gh/oeg-upm/tada-qq/branch/master/graph/badge.svg?token=I9KKJBPLXY)](https://codecov.io/gh/oeg-upm/tada-qq)

[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)


# tada-num-dist
TADA for numeric column. It focuses on distributions to label numeric columns in tabular data.

## Datasets
### Olympic Games Dataset

The data is available here: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1408562.svg)](https://doi.org/10.5281/zenodo.1408562)

We have a script to download the data automatically here `scripts/olympic-download.sh` 
You can run it as follows:```sh scripts/olympic-download.sh```

<!--
## Data
1. Download the csv files from here: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1408562.svg)](https://doi.org/10.5281/zenodo.1408562)
1. Create a folder `local_data/olympic_games/data`
1. Put the csv files of the Olympic games inside it.
1. Put the `meta.csv` in `local_data/olympic_games`
-->

#### To cite the Olympic Games dataset
```
@dataset{alobaid_ahmad_2018_1408562,
  author       = {Alobaid, Ahmad and
                  Corcho, Oscar},
  title        = {Olympic Games 2020},
  month        = sep,
  year         = 2018,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.1408562},
  url          = {https://doi.org/10.5281/zenodo.1408562}
}
```

### T2Dv2
#### Automatic
To download and transform the data automatically, you can use [this](https://github.com/oeg-upm/ttla/blob/master/data/preprocessing.py)
script. 

#### Manual
* [T2Dv2_typology.csv](https://github.com/oeg-upm/ttla/blob/master/meta/T2Dv2_typology.csv)
* [T2Dv2](http://webdatacommons.org/webtables/extended_instance_goldstandard.tar.gz)

#### Extra preprocessing
The application expects to have a folder named `csv` inside the T2Dv2 which includes the files in csv format. You can use the script `scripts/json_to_csv.py` to do that.


## Run Experiments
### Semantic labelling
#### Olympic Games
```
python -m experiments.olympic
```
#### T2Dv2

Arguments
```
optional arguments:
  -h, --help            show this help message and exit
  -e {mean_err,mean_sq_err}, --err-meth {mean_err,mean_sq_err}
                        Functions to computer errors.
  -o {true,false}, --outlier-removal {true,false}
                        Whether to remove outliers or not
```

Sample:
```
python -m experiments.t2dv2 -e mean_err -o true
```

```
python -m experiments.t2dv2 -e mean_sq_err -o true
```


```
python -m experiments.t2dv2 -e mean_err mean_sq_err mean_sqroot_err -o true --estimate True False
```


# Results - T2Dv2
## T2Dv2 Mean Error
![t2dv2.svg](t2dv2-mean-err.svg) 

## T2Dv2 Mean Square Error
![t2dv2.svg](t2dv2-mean-sq-err.svg) 


## Comparison of both

## Remove Outliers
|Quantile Prediction	|Error Function	|Precision	|Recall	|F1	|
|:------:|:------:|:---------:|:------:|:---:|
|estimate	|mean_err	|0.49	|0.84	|0.62	|
|estimate	|mean_sq_err	|0.50	|0.84	|0.63	|
|estimate	|mean_sqroot_err	|0.51	|0.85	|0.64	|
|exact	|mean_err	|0.45	|0.83	|0.58	|
|exact	|mean_sq_err	|0.49	|0.84	|0.62	|
|exact	|mean_sqroot_err	|0.39	|0.81	|0.53	|


## Raw
|Quantile Prediction	|Error Function	|Precision	|Recall	|F1	|
|:------:|:------:|:---------:|:------:|:---:|
|estimate	|mean_err	|0.53	|0.85	|0.65	|
|estimate	|mean_sq_err	|0.53	|0.85	|0.65	|
|estimate	|mean_sqroot_err	|0.53	|0.85	|0.65	|
|exact	|mean_err	|0.53	|0.85	|0.65	|
|exact	|mean_sq_err	|0.53	|0.85	|0.65	|
|exact	|mean_sqroot_err	|0.50	|0.84	|0.63	|


<!--
## Diffs between the gold standard and predicted properties

[using mean error](experiments/diffs/t2dv2-mean-err)

[using square mean error](experiments/diffs/t2dv2-mean-sq-err)

-->

## Number of data points vs performance score
### Outlier Removal
![datapoints.svg](t2dv2-err-methods.svg)

### Raw
![datapoints.svg](t2dv2-err-methods-raw.svg)