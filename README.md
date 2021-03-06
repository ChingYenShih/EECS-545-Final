# Depth Completion from Color Image and Sparse LiDAR Data
This project aims to complete depth from color image and sparse LiDAR data. There are local pathway (to extract local features) and global pathway (to extract global features) in the model. In the end of the model, the results from local pathway and global pathway are merged together based on self-learned weight. The detail implementation is [here](https://github.com/cyshih704/Depth-Completion/blob/master/report/DepthCompletion.pdf).


## Visualization
![image](https://github.com/cyshih704/Depth-Completion/blob/master/figure/merged.png)


## Requirements
* Python 3.6.8
```
pip3 install -r requirements.txt
```

## Data Preparation
- Download the [KITTI Depth](http://www.cvlibs.net/datasets/kitti/eval_depth.php?benchmark=depth_completion) Dataset from their website.
- Use the following scripts to extract corresponding RGB images from the raw dataset. 
```bash
./download/rgb_train_downloader.sh
./download/rgb_val_downloader.sh
```
* The overall code, data, and results directory is structured as follows
  * data_depth_annotated: ground truth data (dense depth)
  * data_depth_velodyne: sparse data (LiDAR)
  * data_rgb: RGB image
  * data_depth_annotated: Used to train surface normals, and generated from **data_depth_annotated** by using **generate_normals.py**

```
.
├── KITTI_data
|   ├── data_depth_annotated
|   |   ├── train
|   |   |   ├── 2011_09_26_drive_0001_sync
|   |   |       ├── proj_depth
|   |   |           ├── groundtruch
|   |   |               ├── image02
|   |   |               ├── image03
|   |   ├── val
|   |   |   ├── (the same as train)
|   ├── data_depth_velodyne
|   |   ├── train
|   |   |   ├── 2011_09_26_drive_0001_sync
|   |   |       ├── proj_depth
|   |   |           ├── velodyne_raw
|   |   |               ├── image_02
|   |   |               ├── image_03
|   |   ├── val
|   |   |   ├── (the same as train)
|   ├── data_rgb
|   |   ├── train
|   |   |   ├── 2011_09_26_drive_0001_sync
|   |   |       ├── image_02
|   |   |       ├── image_03
|   |   ├── val
|   |   |   ├── (the same as train)
|   ├── data_depth_normals
|   |   ├── (the same as data_depth_annotated)
|   └── depth_selection
|   |   ├── test_depth_completion_anonymous
|   |   ├── test_depth_prediction_anonymous
|   |   ├── val_selection_cropped

```

### Path setting
Please set the path in the **env.py** first

```
SAVED_MODEL_PATH = './saved_model' # save model in this directory
KITTI_DATASET_PATH = /PATH/TO/KITTI_data/ # path to KITTI_data as structured in the above
PREDICTED_RESULT_DIR = './predicted_dense' # path to save predicted figures (used in test.py)
```

## Usage

### Train and validation
```
python3 main.py -b <BATCH_SIZE> -e <EPOCH> -m <SAVED_MODEL_NAME> -l <MODEL_PATH> -n <NUM_DATA> -cpu
    -b <BATCH_SIZE>
        batch size used for training and validation
    -e <EPOCH>
        the number of epoch for training and validation
    -m <SAVED_MODEL_NAME>
        the model name (be saved in SAVED_MODEL_PATH)
    -l <MODEL_PATH>
        specified the model path if you want to load previous model
    -n <NUM_DATA>
        the number of data used for training. (set -1 if you want to use all the training data (85898))
    -cpu
        if you want to use CPU to train
```


### Test
Test on **depth_selection/val_selection_cropped** data
```
python3 test.py -m <MODEL_PATH> -n <NUM_DATA> -cpu
    -n <NUM_DATA>
        the number of data used for testing. (set -1 if you want to use all the testing data (1000))
    -m <MODEL_PATH>
        the path of loaded model
    -cpu
        if you want to use CPU to test
    -s
        if you want to save predicted figure in PREDICTED_RESULT_DIR
```

### Test a pair of inputs
Run a pair of rgb and lidar image as input, and then save the predicted dense depth
```
python3 test_a_pair.py --model_path </PATH/TO/PRETRAIN_MODEL> --rgb <PATH/TO/RGB_IMAGE> --lidar <PATH/TO/LIDAR_IMAGE>
                       --saved_path </SAVED_FIGURE/PATH>
    --model_path <MODEL_PATH>
        the path of pretrained model  
    --rgb <PATH>
        the path of rgb image
    --lidar <PATH>
        the path of lidar image
    --saved_path <PATH>
        the path of saved image
```


## Tensorboard Visualization
```
tensorboard --logdir runs/
```

## Citation 
```
@InProceedings{Qiu_2019_CVPR,
author = {Qiu, Jiaxiong and Cui, Zhaopeng and Zhang, Yinda and Zhang, Xingdi and Liu, Shuaicheng and Zeng, Bing and Pollefeys, Marc},
title = {DeepLiDAR: Deep Surface Normal Guided Depth Prediction for Outdoor Scene From Sparse LiDAR Data and Single Color Image},
booktitle = {The IEEE Conference on Computer Vision and Pattern Recognition (CVPR)},
month = {June},
year = {2019}
}
@article{chenlearning,
  title={Learning Joint 2D-3D Representations for Depth Completion},
  author={Chen, Yun and Yang, Bin and Liang, Ming and Urtasun, Raquel}
}
```

