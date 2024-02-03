# Pre-Operative Planning System for Neuromodulation Surgery for Spinal Cord Injury Rehabilitation

This project is about the automatic labeling for MRI to CT co-registration as part of the pre-operative computational pipeline for neuromodulation surgery for spinal cord injury rehabilitation.

***Authors: Ismail Benkirane & Sergio Hernandez***  
***Date: 14/12/2022***

## Table of contents
* [Introduction](##Introduction)
* [Setup](##Setup)
* [Data Preprocessing](##Data preprocessing)
* [Running the Algorithm](##Running the algorithm)
* [Visualizing the results](##Visualizing the results) 

## Introduction

Magnetic Resonance Imaging and CT scans are two types of medical imaging methods that give access to different information.
Indeed, images acquired during CT scans have the advantage of giving access to a clear and precise segmentation
of vertebrae. This is not the case for images acquired during MRI. On the other hand, MRI images offer access to
information about nerves and roots which we can't have using CT scans. These two acquisition methods may be used before
the implantation of the device, however, once the device is implanted on the spinalcord, MRI scans are no longer possible.
This is why it is very important for the scope of this project, to have a good co-registration between the CT and MRI images.

## Setup
### Dependencies 
In order for the python script and the co-registration functions to run, the following dependencies need to be 
downloaded in your environment : 
- [numpy](https://numpy.org) - version 1.21.5
- [nibabel](https://pypi.org/project/nibabel/) - version 4.0.2
- [matplotlib](https://docs.python.org/3/library/math.html) - version 3.5.1
- [cc3d](https://pypi.org/project/connected-components-3d/) - version 3.10.2
- [fsleyes](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FSLeyes) - version 1.5.0
- [spinal_cord_toolbox](https://spinalcordtoolbox.com) - version 5.7.0

### Directory Structure
I recommend having the following directory structure:
```
folder:
├───code
        main.py
        README.md
        main.ipynb
        utils.py
        02_co_registration_function_determination.sh
        03_applying_co_registration_function.sh
        04_run_cleaning_seg_post_co_registration.sh
        05_run_cleaning_seg_non_binary.sh   
├───data
        CT_image.nii.gz
        CT_seg_bin.nii.gz
        CT_seg_multi.nii.gz
        MRI_image.nii.gz
        MRI_Disks.nii.gz
        MRI_vertebrae.nii.gz
```

## Data preprocessing

### Orientation

Most of the time, MRI and CT images come in different orientations:

![Image orientation](https://www.slicer.org/w/img_auth.php/2/22/Coordinate_sytems.png)

In neuroimaging, the anatomical coordinate system is defined with respect to the human whose brain is being scanned. 
Hence the 3D basis is defined along the anatomical axes of anterior-posterior, inferior-superior, and left-right. 
However, we can find different 3D basis such as:

- LPS (Left-Posterior-Superior) orientation :
  - from right towards left
  - from anterior towards posterior
  - from inferior towards superior
- RAS (Right-Anterior-Superior)
  - from left towards right
  - from posterior towards anterior
  - from inferior towards superior

All 3D bases are equally useful and logical. It is just necessary to know to which basis an image is referenced and normalize
this orientation across all used images. In the scope of this project, we used the following orientation:

- RPI (Right-Posterior-Inferior)
  - from left to right
  - from anterior to posterior
  - from superior to inferior

To identify which orientation the data you need to analyze has and change it if needed, you can use 
the two following functions from the [spinal_cord_toolbox](https://spinalcordtoolbox.com).

- In order to determine which orientation an image has :
  - `sct_image -i 'image_path' -getorient`
- In order to change it if needed to the RPI orientation:
  - `sct_image -i 'image_path' -setorient 'RPI'`

Now that all images have the same orientation, you can run the script. But before, an additional preprocessing step has
to be done in order to have better results, and this is upsampling. 

### Upsampling

At first, we processed and used data with the standard sampling size. However, we quickly noticed that
the CT images had more samples than MRI images which led to good results but not as good as we wanted them.
A solution to this issue is to simply upsample the MRI images. Indeed, we try to give the MRI images the same number
of samples as the CT images. To do that, we will again use the [spinal_cord_toolbox](https://spinalcordtoolbox.com). But
first, we have to assess the sampling size of the CT image. The steps are the following:
- Access information about the CT images using fsleyes (`fsleyes \path\to\CT\image`)
- Use the information option in the fsleyes menu to access the sampling size : pixdim1, pixdim2, pixdim3
<img src="/Users/ismail/switchdrive/PDS/folder/images/parameters.png" alt="Alt text" title="<dimension infomation for a CT image>">
- Finally, you can upsample the MRI data using the following command:
```
sct_resample -i \path\to\MRI\img -mm pixdim1xpicdim2xpixdim3
```

By upsampling the data, the computation time is a bit longer but the results are clearly better.


## Running the algorithm

### Step 1 - _Labelling script_

The first step of the algorithm's pipeline is to run the `main.py` script. It takes as inputs 5 parameters:

- `<input_disk_img>`: the path to the MRI disk image
- `<input_MRI_img>`: the path to the MRI vertebrae image
- `<input_CT_img>`: the path to the CT vertebrae image
- `<output_path>`: the output path for the two output images
- `<vertebrae>`: It can be either :
  - Desired labelled vertebrae (Separated by a blank space) such as 'T1' 'T5'.
  - The name of the study such as 'hemo', 'hemon', 'stimo'.
  - It can also be 'all' if we want to put labels on all vertebrae

Then, to run it, use the following structure:

`main.py -idisks <input_disk_img> -imri <input_MRI_img> -ict <input_CT_img> -o <output_path> -v <vertebrae>`

This script will output two images that will be used for the CT to MRI co-registration:
- `MRI_labels.nii.gz`
- `CT_labels.nii.gz`

### Step 2 - _Computing the co-registration function_
Now that the two labelled images outputted by the previous script are available, you can proceed with the co-registration. 
First, you have to compute the co-registration function between CT and MRI images. 
To do that, run the following lines on the terminal:
```
chmod u+x 02_co_registraion_function_determination.sh

./02_co_registration_function_determination.sh <CT_img_path> <CT_seg_path> <CT_label_path> <MRI_img_path> <MRI_seg_path> <MRI_label_path> <OUTPUT_folder>
```
This script simply runs the [the spinal_cord_toolbox](https://spinalcordtoolbox.com) function `sct_register_multimodal`, 
giving it the following parameters: 
- `-param step=0,type=label,dof=Tx_Ty_Tz_Ry:step=1,type=seg,algo=affine`

As an output, you will obtain 2 warp functions (co-registration functions):
- `CT2MRI.nii.gz`
- `MRI2CT.nii.gz`

### Step 3 - _Applying the co-registration function_

Using the warp functions computed before, you can apply the co-registration. To do that, run the following lines on the terminal:
```
chmod u+x 03_applying_co_registration_function.sh

./03_applying_co_registration_function.sh <ORIG_img_path> <DEST_img_path> <WARP_field_path> <OUTPUT_img_path>
```
For example, if we want a co-registration from the CT space to the MRI space:
- `<ORIG_img_path>` is the path to the segmented CT image.
- `<DEST_img_path>` is the path to the MRI image. 
- `<WARP_field_path>` is the path to the `CT2MRI.nii.gz` file.

### Step 4 (Optional but recommended) - _Binarizing the co-registration results_

This step enables to binarize the co-registered binary segmentation of the vertebrae from CT scans co-registered 
in the MRI space. The output will be a binary image, where 1 represent the tissue and 0 the rest. To do it, run the 
following lines on the terminal :
```
chmod u+x 04_run_cleaning_seg_post_co_registration.sh

./04_run_cleaning_seg_post_co_registration.sh <COREGISTERED_seg_path> <OUTPUT_binary_file_path>
```
where :
- `<COREGISTERED_seg_path>` is the path to the .nii.gz file computed in step 3.
- `<OUTPUT_binary_file_path>` is the path where we want the binary output file to be.

### Step 5 (Optional but recommended) - _Cleaning the co-registered non-binary segmentation_
This step enables to clean the co-registered non-binary segmentation of the Vertebrae from CT scans co-registered in 
the MRI space. The output will be a multi-label co-registered segmentation image. To do it, run the following lines on 
the terminal: 
```
chmod u+x 05_run_cleaning_seg_non_binary.sh 

./05_run_cleaning_seg_non_binary.sh <COREGISTERED_seg_path> <OUTPUT_multi_label_file_path>
```
where :
- `<COREGISTERED_seg_path>` is the path to the .nii.gz file computed in step 3.
- `<OUTPUT_multi_label_file_path>` is the path where we want the multi-label co-registered segmentation file output file to be.

## Visualizing the results

To visualize the results of the co-registration, you can use [fsleyes](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FSLeyes). The 
line to run on the terminal is:
```
fsleyes <COREGISTERED_seg_path> <MRI_seg_path>
```
where:
- `<COREGISTERED_seg_path>` is the path to the .nii.gz file computed in step 3.
- `<MRI_seg_path>` is the path to the segmented vertebrae image. 

