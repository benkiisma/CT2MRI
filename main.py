# -*- coding: utf-8 -*-
"""
Script to create labels that will be used for the coregistration of the MRI to CT images.
 Inputs:
- Segmented Disk image `.nii.gz`
- MRI Segmented Vertebrae image `.nii.gz`
- CT Segmented Vertebrae image `.nii.gz`
- Output path
- Labels (Optional)
Outputs:
- 2 files in the output folder as `.nii.gz`
@author: Benkirane Ismail
"""

utils = "/Users/ismail/switchdrive/PDS/code/utils.py"
exec(compile(open(utils, "rb").read(), utils, 'exec'))

def main(argv):
    
    input_disk_img = 'none'
    input_MRI_img = 'none'
    input_CT_img = 'none'
    output_path = 'none'
    vertebrae= 'none'

    for a in range(len(argv)):
        if argv[a] == '-h':
            print('seglabeling.py -idisks <input_disk_img> -imri <input_MRI_img> -ict <input_CT_img> -o <output_path> -v <2_vertebrae>')
            sys.exit()
        if len(sys.argv) < 11:
            print("No vertebrae were selected. Please enter the vertebrae you want to use")
            print('seglabeling.py -idisks <input_disk_img> -imri <input_MRI_img> -ict <input_CT_img> -o <output_path> -v <2_vertebrae>')
            sys.exit()  
        else:
            if argv[a] == "-idisks":
                input_disk_img = argv[a+1]
            elif argv[a] == "-imri":
                input_MRI_img = argv[a+1]
            elif argv[a] == "-ict":
                input_CT_img = argv[a+1]
            elif argv[a] == "-o":
                output_path = argv[a+1]
            elif argv[a] == "-v":
                vertebrae = []
                if argv[a+1] == "hemon":
                    vertebrae.append("L2")
                    vertebrae.append("T12")
                    vertebrae.append("T7")
                elif argv[a+1] == "hemo":
                    vertebrae.append("L5")
                    vertebrae.append("L1")
                    vertebrae.append("T7")
                elif argv[a+1] == "stimo":
                    vertebrae.append("L2")
                    vertebrae.append("T10")
                    vertebrae.append("T7")
                elif argv[a+1] == "all":
                    print("all vertebrae have been chosen")
                else :
                    vertebrae.append(argv[a+1])
                    for i in range(len(sys.argv)-11):
                        vertebrae.append(argv[a+2+i])

    if input_disk_img=='none':
        print('seglabeling.py -idisks <input_disk_img> -imri <input_MRI_img> -ict <input_CT_img> -o <output_path> -v <vertebrae>')
        sys.exit()
    if input_MRI_img=='none':
        print('seglabeling.py -idisks <input_disk_img> -imri <input_MRI_img> -ict <input_CT_img> -o <output_path> -v <vertebrae>')
        sys.exit()
    if input_CT_img=='none':
        print('seglabeling.py -idisks <input_disk_img> -imri <input_MRI_img> -ict <input_CT_img> -o <output_path> -v <vertebrae>')
        sys.exit()
    if output_path=='none':
        print('seglabeling.py -idisks <input_disk_img> -imri <input_MRI_img> -ict <input_CT_img> -o <output_path> -v <vertebrae>')
        sys.exit()

    if os.path.exists(input_disk_img) and os.path.exists(input_MRI_img) and os.path.exists(input_CT_img):
        main_labeling(input_disk_img, input_MRI_img, input_CT_img, output_path,vertebrae)
    else:
        if os.path.exists(input_disk_img)==0:
            print('Error: Input Image ' + input_disk_img + ' does not exist!')
            sys.exit()
        if os.path.exists(input_MRI_img)==0:
            print('Error: Input Image ' + input_MRI_img + ' does not exist!')
            sys.exit()
        if os.path.exists(input_CT_img)==0:
            print('Error: Input Image ' + input_CT_img + ' does not exist!')
            sys.exit()

def main_labeling(input_disk_img, input_MRI_img, input_CT_img, output_path, vertebrae):

    # load the vertebrae and the Disk image from MRI
    print("Loading the MRI Vertebrae and Disks images...")
    img_vertebrae = load_image_np_data(input_MRI_img)
    img_disks = load_image_np_data(input_disk_img)
    #Create the segmented MRI image and compute the volume corresponding to each vertebra
    print("Creating the segmented MRI image...")
    img_seg_MRI,all_vol_MRI, seg_labels_MRI = MRI_image_treatment(img_disks,img_vertebrae)  
    
    #load the vertebrae segmentation image from CT
    print("Loading the CT image...")
    img_seg_CT = load_image_np_data(os.path.normpath(input_CT_img))
    #Store the labels and compute the volume corresponding to each vertebra
    seg_labels_CT, all_vol_CT = CT_image_treatment(img_seg_CT)
    
    #Isolating the vertebrae that will be used to set the labels
    print("Label Selection...")
    label, volume_MRI, volume_CT = label_selection(seg_labels_MRI, seg_labels_CT, all_vol_MRI, all_vol_CT, vertebrae)
    
    #Creating the labelled images
    print("Creation of the labelled image...")
    label_MRI_img = img_label(img_seg_MRI, label)
    label_CT_img = img_label(img_seg_CT, label)
    
    #Saving the MRI labelled image
    print("Saving the MRI image...")
    img_final_MRI = final_image(img_seg_MRI, label_MRI_img, volume_MRI, label)
    save_image_np_data(img_final_MRI, input_MRI_img, output_path, True)  
    
    #Saving the CT labelled image
    print("Saving the CT image...")
    img_final_CT = final_image(img_seg_CT, label_CT_img, volume_CT, label)
    save_image_np_data(img_final_CT, input_CT_img, output_path, False)
    
if __name__ == "__main__":
    main(sys.argv[1:])
