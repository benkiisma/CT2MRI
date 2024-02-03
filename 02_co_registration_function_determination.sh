#!/bin/bash
# Script to determine the co-registration function between a T2w MRI acquired to segment the bones and discs
# and a CT scan.
# Bone segmentations are present in both.
# Labels are drawn.
# Parameters are:
# CT_IMG path, CT_SEG path, CT_LABEL path
# T2w_IMG path, T2w_SEG path, T2w_LABEL path
# Author: Sergio Daniel Hernandez Charpak

# Input paths
IMG_ORIG=$(realpath ${1})
SEG_ORIG=$(realpath ${2})
LAB_ORIG=$(realpath ${3})
IMG_DEST=$(realpath ${4})
SEG_DEST=$(realpath ${5})
LAB_DEST=$(realpath ${6})
OUTPUT_FOLDER=$(realpath ${7})

# Output files determination
EXT_FILES=".nii.gz"
IMG_ORIG_NO_EXT=$(basename -s $EXT_FILES $IMG_ORIG)
IMG_DEST_NO_EXT=$(basename -s $EXT_FILES $IMG_DEST)
FORWARD_WARP_NAME="CT2MRI"$EXT_FILES
INVERSE_WARP_NAME="MRI2CT"$EXT_FILES
CO_REGISTERED_ORIG_IN_DEST=$IMG_ORIG_NO_EXT"_reg"$EXT_FILES
FORWARD_WARP_PATH=$OUTPUT_FOLDER"/"$FORWARD_WARP_NAME
INVERSE_WARP_PATH=$OUTPUT_FOLDER"/"$INVERSE_WARP_NAME
CO_REGISTERED_ORIG_IN_DEST_PATH=$OUTPUT_FOLDER"/"$CO_REGISTERED_ORIG_IN_DEST

mkdir -p $OUTPUT_FOLDER

# Determination of the co-registration function
sct_register_multimodal -d $IMG_DEST -i $IMG_ORIG -dlabel $LAB_DEST -ilabel $LAB_ORIG -dseg $SEG_DEST -iseg $SEG_ORIG -o $CO_REGISTERED_ORIG_IN_DEST_PATH -owarp $FORWARD_WARP_PATH -owarpinv $INVERSE_WARP_PATH -param step=0,type=label,dof=Tx_Ty_Tz_Ry:step=1,type=seg,algo=affine
