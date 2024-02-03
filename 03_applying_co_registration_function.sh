#!/bin/bash
# Script to apply the co-registration function between a T2w MRI acquired to segment the bones and discs
# and a CT scan.
# Parameters are:
# ORIG_IMG path, DEST_IMG path, WARP_FIELD_path, OUTPUT_IMG_path
# Author: Sergio Daniel Hernandez Charpak

# Input
IMG_ORIG=$(realpath ${1})
IMG_DEST=$(realpath ${2})
WARP_FIELD=$(realpath ${3})
OUTPUT_IMG=$(realpath ${4})

sct_apply_transfo -i $IMG_ORIG -d $IMG_DEST -w $WARP_FIELD -o $OUTPUT_IMG
