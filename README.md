# SCUBANetV2

ScubaNetV2 is a SCUBA gesture object detection dataset created using weak supervision techniques. Two weak supervision sources are used to create the object detection labels that can be used to train an object detection model. 

1. Manualy Labelled Image Classification - this weak supervision source provides the class label used in the resulting dataset
2. Machine Labelled Scuba Diver Parts (Head, Hands) - this weak supervision source provides the object bounding box

The **gestures** directory contains short video clip of SCUBA divers repeatedly performing a single SCUBA signal (You, Swim, Down, Nine, etc.). Each clip is accompanied by a similarly named **.json** file with per frame gesture classification labels. These classification labels were annotated manually using a simple GUI, see the section **Adding Data** for details on how to provide additional data.

NOTE:: A trained YOLO model that can detect the head and hands of a SCUBA diver is required

## Adding Data

TODO:

## Creating the Dataset

This script combines the data from both weak supervision sources using a variety of heuristics to create a fully labelled object detection database of SCUBA gestures. The generated dataset uses the PASCAL VOC format.

```
usage: create_dataset.py [-h] [--dataset_name DATASET_NAME] [--dataset_dir DATASET_DIR] model_path

positional arguments:
	model_path						Path to ScubaNetV1+ YOLO model

optional arguments:
	-h, --help								show this help message and exit
	--dataset_name DATASET_NAME				Directory to place the new weakly supervised label
	--weak_data WEAK_DATA					Directory where the videos and per frame gesture classifications are stored
```

# Convert to DarkNet Format

To train a YOLO model using the generated dataset it needs to be converted to the DarkNet format. This script adds darknet labels to an
existing PASCAL VOC dataset using YAML description of a YOLO dataset (see scubanetv2.yaml).

```
usage: processXML.py [-h] [--dataset_yaml DATASET_YAML] [--dataset_dir DATASET_DIR]

optional arguments:
	-h, --help									show this help message and exit
	--dataset_yaml DATASET_YAML					YAML description of YOLO dataset
	--dataset_dir DATASET_DIR					Pascal VOC directory (annotations and images folders)
```

# Culling Excess Labels

The resulting datset often has a non-uniform distribution of labels across the set of gesture classes. Generally speaking a uniform distribution is desired for best results. This script randomly culls image labels from each class that has more labels than a configurable
maximum. The number of idle labels to retain is configurable seperatly.

```
usage: cull.py [-h] [--dataset_dir DATASET_DIR] [--idle_limit IDLE_LIMIT] limit

positional arguments:
	limit						Maximum number of class labels to retain (if Zero dont cull just count)

optional arguments:
	-h, --help						show this help message and exit
	--dataset_dir DATASET_DIR		Directory where annotations and images folders were created
	--idle_limit IDLE_LIMIT			Maximum number of idle labels to retain

```

## Spilting to Test/Train/Validate

This script partitions a dataset into three subsets (test, train, validate). 

```
usage: split.py [-h] [--dataset_dir DATASET_DIR] [--train_ratio TRAIN_RATIO]
                [--val_ratio VAL_RATIO] [--test_ratio TEST_RATIO]

optional arguments:
	-h, --help							show this help message and exit
	--dataset_dir DATASET_DIR			Directory where annotations and images folders were created
	--train_ratio TRAIN_RATIO			Percentage of data to use as a training set
	--val_ratio VAL_RATIO				Percentage of data to use as a validation set
	--test_ratio TEST_RATIO				Percentage of data to use as a testing set

```

## Training

This will train the chosen model on the generated SCUBANetV2 dataset. The script
will run and output training and validation metrics as well as a number of checkpoint models. You will need
the model name **best.pt**

```
usage: train.py [-h] [--yolo_model YOLO_MODEL] [--cfg_file CFG_FILE] yaml_file

positional arguments:
  yaml_file			ultralytics dataset description file

optional arguments:
	-h, --help				show this help message and exit
	--yolo_model YOLO_MODEL	YOLO version to train
	--cfg_file CFG_FILE		YOLO hyperparameters configuration 
```


