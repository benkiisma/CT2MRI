#!/bin/bash
# Script to clean the co-registered non-binary segmentation of the Vertebrae from CT scans
# co-registered in the MRI space.
# The pipeline goes as follows:
# 1. From the larges value (most caudal) to the smallest value (more rostral), isolate one by one the
# segmented vertebrae.
# Parameters:
# COREGISTERED_SEGMENTATION_OUTPUT_PATH: Path to the .nii.gz file corresponding to the co-registered binary segmentation.
# MULTI_LABEL_COREGISTERED_SEGMENTATION_OUTPUT_FOLDER_PATH: Path to the output .nii.gz file.
# Outputs:
# A binary segmentation for each vertebrae as .nii.gz
# Value where there is tissue: 1. The rest is set to 0.
# Author: Sergio Daniel Hernandez Charpak

# Parameters
COREGISTERED_SEGMENTATION_OUTPUT_PATH=$1
MULTI_LABEL_COREGISTERED_SEGMENTATION_OUTPUT_FOLDER_PATH=$(realpath ${2})
#LARGEST_VERT_VALUE=24
#SMALLEST_VERT_VALUE=15
ESPILON="0.4"
#values_array=($(seq $SMALLEST_VERT_VALUE $LARGEST_VERT_VALUE 1.0))
declare -a vert_names_array=("C2" "C3" "C4" "C5" "C6" "C7" "C8" "T1" "T2" "T3" "T4" "T5" "T6" "T7" "T8" "T9" "T10" "T11" "T12" "L1" "L2" "L3" "L4" "L5" "S1")
declare -a values_array=("1" "2" "3" "4" "5" "6" "7" "8" "9" "10" "11" "12" "13" "14" "15" "16" "17" "18" "19" "20" "21" "22" "23" "24" "25")

EXT_FILES=".nii.gz"
TMP_FOLDER="TMP_FOLDER"
TMP_FOLDER_PATH=$MULTI_LABEL_COREGISTERED_SEGMENTATION_OUTPUT_FOLDER_PATH"/"$TMP_FOLDER
# Hidden to the user.
f_no_ext=$(basename -s $EXT_FILES $COREGISTERED_SEGMENTATION_OUTPUT_PATH)

mkdir -p $TMP_FOLDER_PATH

for (( i=0; i<${#values_array[@]}; i++ ));do
    val_vert=${values_array[$i]}
    name_vert=${vert_names_array[$i]}
    value_for_upper_thresh=$(echo "$val_vert + $ESPILON" | bc)
    value_for_lower_thresh=$(echo "$val_vert - $ESPILON" | bc)
    
	echo "Separating "$name_vert" from "$f_no_ext
	output_tmp_image=$TMP_FOLDER_PATH"/"$f_no_ext"_"$name_vert"_tmp"$EXT_FILES
	output_image=$MULTI_LABEL_COREGISTERED_SEGMENTATION_OUTPUT_FOLDER_PATH"/"$f_no_ext"_"$name_vert$EXT_FILES
	sct_maths -i $COREGISTERED_SEGMENTATION_OUTPUT_PATH -o $output_tmp_image -uthr $value_for_upper_thresh
	sct_maths -i $output_tmp_image -o $output_tmp_image -thr $value_for_lower_thresh
    sct_maths -i $output_tmp_image -o $output_tmp_image -bin $value_for_lower_thresh

    # Erode.
    N_EROSIONS=2
    output_tmp_ERODED_NO_EXT=$TMP_FOLDER_PATH"/"$f_no_ext"_"$name_vert"_tmp""_eroded_"$N_EROSIONS
    output_tmp_ERODED_EXT=$output_tmp_ERODED_NO_EXT$EXT_FILES
    sct_maths -i $output_tmp_image -o $output_tmp_ERODED_EXT -erode $N_EROSIONS -shape=disk -dim=2

    # Dilate.
    output_tmp_CLOSED_NO_EXT=$TMP_FOLDER_PATH"/"$f_no_ext"_"$name_vert"_tmp""_closed_"$N_EROSIONS
    output_tmp_CLOSED_EXT=$output_tmp_CLOSED_NO_EXT$EXT_FILES
    sct_maths -i $output_tmp_ERODED_EXT -o $output_tmp_CLOSED_EXT -dilate $N_EROSIONS -shape=disk -dim=2
    # FInal output
    cp $output_tmp_CLOSED_EXT $output_image
    
done
