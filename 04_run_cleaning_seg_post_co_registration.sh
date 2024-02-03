#!/bin/bash
# Script to binarize the co-registered binary segmentation of the Vertebrae from CT scans
# co-registered in the MRI space.
# The pipeline goes as follows:
# 1. Binarize the co-registered segmentation using 0.1 as threshold. (Using 0.0 creates artifacts)
# Parameters:
# COREGISTERED_SEGMENTATION_OUTPUT_PATH: Path to the .nii.gz file corresponding to the co-registered binary segmentation.
# BINARY_COREGISTERED_SEGMENTATION_OUTPUT_PATH: Path to the output .nii.gz file.
# Outputs:
# The binary segmentation as .nii.gz
# Value where there is tissue: 1. The rest is set to 0.
# Author: Sergio Daniel Hernandez Charpak

# Parameters
COREGISTERED_SEGMENTATION_OUTPUT_PATH=$1
BINARY_COREGISTERED_SEGMENTATION_OUTPUT_PATH=$2
# Hidden to the user.
EXT_FILES=".nii.gz"
BINARIZE_VALUE=0.1
N_EROSIONS=2
# Temp Results
f_no_ext=$(basename -s $EXT_FILES $COREGISTERED_SEGMENTATION_OUTPUT_PATH)
f_folder=$(dirname $COREGISTERED_SEGMENTATION_OUTPUT_PATH)
TMP_FOLDER="TMP_FOLDER"
TMP_FOLDER_PATH=$f_folder"/"$TMP_FOLDER
mkdir -p $TMP_FOLDER_PATH
tmp_ext="_TMP"
f_tmp_no_ext=$f_no_ext$tmp_ext
f_tmp=$f_tmp_no_ext$EXT_FILES
f_tmp_path=$TMP_FOLDER_PATH"/"$f_tmp
# Binarizing the segmentation
sct_maths -i $COREGISTERED_SEGMENTATION_OUTPUT_PATH -bin $BINARIZE_VALUE -o $f_tmp_path
# Erode.
output_tmp_ERODED_NO_EXT=$f_tmp_no_ext"_eroded_"$N_EROSIONS
output_tmp_ERODED=$output_tmp_ERODED_NO_EXT$EXT_FILES
output_tmp_ERODED_PATH=$TMP_FOLDER_PATH"/"$output_tmp_ERODED
sct_maths -i $f_tmp_path -o $output_tmp_ERODED_PATH -erode $N_EROSIONS -shape=disk -dim=2
# Dilate.
output_tmp_CLOSED_NO_EXT=$f_tmp_no_ext"_closed_"$N_EROSIONS
output_tmp_CLOSED=$output_tmp_CLOSED_NO_EXT$EXT_FILES
output_tmp_CLOSED_PATH=$TMP_FOLDER_PATH"/"$output_tmp_CLOSED
sct_maths -i $output_tmp_ERODED_PATH -o $output_tmp_CLOSED_PATH -dilate $N_EROSIONS -shape=disk -dim=2
# Final output
cp $output_tmp_CLOSED_PATH $BINARY_COREGISTERED_SEGMENTATION_OUTPUT_PATH
# Removes the tmp folder
rm -r $TMP_FOLDER_PATH