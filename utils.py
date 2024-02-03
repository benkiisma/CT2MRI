# General purpose imports to handle paths, files etc
import os

#General libraries for data manipulation
import numpy as np
import nibabel as nib
from matplotlib import pyplot as plt
import math
import cc3d
import sys

def load_image(image_path):
    """
    Returns the image_src using nibabel
    @param: image complete path
    @returns: the image data as a numpy array
    """
    image_src = nib.load(image_path)
    
    return image_src

def load_image_np_data(image_path):
    """
    Returns the image_data as a numpy array given the path
    @param: image complete path
    @returns: the image data as a numpy array
    """
    image_src = load_image(image_path)
    image_data = image_src.get_fdata()
    
    image_data = np.fliplr(image_data)
    image_data = np.transpose(image_data,[1,2,0])
    
    return image_data.copy()

def save_image_np_data(output_array, og_image_path, target_folder_path, MRI):
    """
    Saves image np array as nifti file at og_path location
    @param: output_array: image data as np array
            og_image_path: path to original segmentation nifti image
            target_folder_path: output_array image saved to this location in nifti format
            disks: bool, True if output_array image is disks centroids, False if vertebrae seeds
    @returns: nothing
    """
    og_image = nib.load(og_image_path)
    img_affine = og_image.affine
    img_header = og_image.header
    data = output_array 
    output_image = nib.Nifti1Image(data, img_affine, img_header)
    if MRI:
        nib.save(output_image, os.path.join(os.path.dirname(target_folder_path), 'MRI_labels.nii.gz'))
    else:
        nib.save(output_image, os.path.join(os.path.dirname(target_folder_path), 'CT_labels.nii.gz'))
        
    return

def connected_components(img):
    """
    Run connected components algorithm to label individual disk point clouds
    @param: img: 3D np.array containing segmentation of disks
    @returns: img_cc: 3D np.array image with one label per disk/component
              n_disks: int
    """
    img_cc, n_disks = cc3d.connected_components(np.transpose(img, [1,0,2]), return_N=True)
    img_cc = np.transpose(img_cc, [1,0,2])
    
    return img_cc, n_disks

def group_components(img_cc, n_disks):
    """
    Groups coordinates of each component/disk into a tuple
    @param: img_cc: connected components of disk segmentation
            n_disks: int
    @returns: disk_data: list (length:n_disks) of tuples, each containing the coordinates of a component/disk
    """   
    disks_data = []
    for disk in range(1, n_disks+1):
        idx = np.where(np.isclose(img_cc, np.full(img_cc.shape, disk)))
        disks_data.append(idx)
                
    return disks_data

def find_centroids(disks_data):
    """
    Calculates centroids of each component/disk
    @param: disks_data: list (length:n_disks) of tuples, each containing the coordinates of a component/disk
    @returns: disks_centroids: list of np.array [x,y,z]
    """       
    disks_centroids = []
    for elem in disks_data:
        centroid = np.around(np.average(elem, axis=1))[2]
        disks_centroids.append(centroid.astype(int))
    
    return disks_centroids

def group_target_components(img_seg, labels):
    """
    Groups coordinates of each component/disk into a tuple
    @param: img_seg: image with connected components of vertebrae segmentation (3D np.array)
    @returns: vert_data: list (length:n_vert) of tuples, each tuple: ([x1,x2...], [y1,y2,...], [z1,z2,...]) 
    with coordinates of a component
    """  
    vert_data = []
    for label in labels: 
        idx = np.where(np.isclose(img_seg, np.full(img_seg.shape, label)))
        vert_data.append(idx)
    return vert_data


def vertebrae_seg(img_vertebrae, disks_data, volume):
    """
    Segments the vertebrae image into separate vertebrae using the disks position
    @params: img_vertebrae: MRI image
            disks_data: information about the disks positions 
            volume: Vector containing the relevant volumes for each vertebrae
    @returns: Segmented MRI image with each vertebra labelled.
    """
    image = np.copy(img_vertebrae)
    disk_data_max = np.zeros((len(disks_data)))
    disk_data_min = np.zeros((len(disks_data)))
    SACRAL_LABEL = 25

    for i in range(0, len(disks_data)):
        disk_data_max[i] = max(disks_data[i][1])
        disk_data_min[i] = min(disks_data[i][1])

    for x in range(np.size(image, 0)):
        for y in range(np.size(image, 1)):
            for z in range(np.size(image, 2)):
                if image[x, y, z] == 1:
                    for i in range(1, len(disks_data)):
                        if (y >= disk_data_max[i - 1]) and (y <= disk_data_min[i]):
                            image[x, y, z] = SACRAL_LABEL - i

    for x in range(np.size(image, 0)):
        for y in range(np.size(image, 1)):
            for z in range(np.size(image, 2)):
                if (image[x, y, z] == 1) and (y > disk_data_max[0]):
                    image[x, y, z] = 0
                if (image[x, y, z] == 1) and (y < disk_data_max[0]):
                    image[x, y, z] = SACRAL_LABEL

    image[image == 1] = 0

    return image

def ref_coord (img,volume):
    """
    Calculates the coordinates of the reference point(label) that will be used
    @param: img: image of a single vertebrae
            volume: Corresponding volume
    @returns: Vector containing the x and y coordinates of the label points
    """
    
    lim = round(2*np.size(img,0)/3)
    img = img[:lim,:,volume]
    x_min = np.min(np.nonzero(img)[1][:])
    x_max = np.max(np.nonzero(img)[1][:])
    x_mid = round((x_max+x_min)/2)
    new_img = img[:,x_mid]
    y_coord = np.min(np.nonzero(new_img)[0][:])
    x_coord = x_mid
    
    return [x_coord, y_coord]

def find_labels(img):
    """
    Computes the labels for vertebrae
    @params: segmented image
    @returns: Vectore containing the labels
    """
    labels = np.unique(img)
    labels = labels[1:]
    labels = np.flip(labels).astype(int)
    
    return labels

def MRI_image_treatment(img_disks,img_vertebrae):
    """
    Computes the relevant volumes for each vertebra and their labels. It also segments the vertebrae image 
    @params: img_disks: Loaded Disk Image
             img_vertebrae: Loaded Vertebrae MRI image
    @returns: img_seg: Segmented MRI image
              volumes: vector of relevant volumes
              seg_labels: number corresponding to the available vertebrae
    """
    img_cc, n_disks = connected_components(img_disks)
    disks_data = group_components(img_cc, n_disks)
    volumes = find_centroids(disks_data)
    img_seg = vertebrae_seg(img_vertebrae, disks_data, volumes)
    seg_labels = find_labels(img_seg)
    
    return img_seg, volumes, seg_labels

def CT_image_treatment(img):
    """
    Computes the relevant volumes for each vertebra and stores the labels
    @params: img: Segmented CT image
    @returns: seg_labels: labels of the CT image
              volumes: vector of relevant volumes
    """
    seg_labels = find_labels(img)
    volumes = find_centroids(group_target_components(img, seg_labels))
    
    return seg_labels, volumes

def label_selection(labels_MRI, labels_CT,volume_MRI,volume_CT,vertebrae):
    """
    Based on the labels entered, place the label points on the corresponding vertebra and select the corresponding volume
    @params: labels_MRI: Labels of the segmented MRI image
             labels_CT: Labels of the segmented CT image
             volume_MRI: vector of the volumes for the MRI image 
             volume_CT: vector of the volumes for the CT image 
             vertebrae: list of the chosen vertebrae.
    @returns: label: Labels corresponding to the chosen vertebrae 
              vol_MRI: Volumes corresponding to the chosen vertebrae for MRI 
              vol_CT: Volumes corresponding to the chosen vertebrae for CT
    """
    nb_labels_MRI = len(labels_MRI)
    nb_labels_CT = len(labels_CT)

    if (nb_labels_MRI <= nb_labels_CT):
        nb_labels = nb_labels_MRI
        labels = labels_MRI
    else:
        nb_labels = nb_labels_CT
        labels = labels_CT

    dict_label = {}
    for i in range(nb_labels):
        if i == 0:
            vert = 'S1'
        elif 0<i<6:
            vert = 'L'+str(6-i)
        elif 5<i<18:
            vert = 'T'+str(18-i)
        else: 
            vert = 'C'+25-i
        dict_label[vert] = i
        
    all_vertebrae = dict_label.keys()
    print("The vertebrae accessible for this patient are: "+str(list(all_vertebrae)))
    
    vert = []
    
    if vertebrae == []:
        for key in dict_label.keys():
            vert.append(key)  
    else:
        if type(vertebrae[0]) == int:
            for i in range(len(vertebrae)):
                if vertebrae[i] < nb_labels:
                    vert.append(list(dict_label.keys())[vertebrae[i]])
                else:
                    vert.append(list(dict_label.keys())[-1])
        else:
            for i in range(len(vertebrae)): 
                if vertebrae[i] not in dict_label:
                    print("The vertebra " +str(vertebrae[i]) +" you indicated is not present for this subject")
                    sys.exit()
                    
            vert = vertebrae
        
    print("The vertebrae used to position the label points are: "+str(vert))
    
    label = []
    vol_MRI = []
    vol_CT = []
    for i in range(len(vert)):
        label.append(labels[dict_label[vert[i]]])
        vol_MRI.append(volume_MRI[dict_label[vert[i]]])
        vol_CT.append(volume_CT[dict_label[vert[i]]])
        
    return label,vol_MRI,vol_CT

def img_label(img_seg, label):
    """
    Labels the relevant vertebrae for the coregistration
    @params: img_seg: Segmented image 
             label: list of the labels of the vertebrae selected to hold the label points.
    @returns: label_img: List containing all the images of the vertebrae selected to hold the label point. 
    """
    label_img = []
    for l in label:
        img_label = np.copy(img_seg)
        img_label[img_label == l] = 100*l
        img_label[img_label < 50] = 0
        img = np.copy(img_label)
        img[img != 100*l] = 0
        label_img.append(img)
    
    return label_img

def final_image(img_seg, label_img, volume, label):
    """
    Computes the final image that can be saved
    @params: img_seg: segmented image
             label_img_1: image of the first vertebrae
             label_img_2: label of the second vertebrae
             volume: Vector containing the volume of each vertebra 
             label: Vector containing the labels of each vertebra
    @returns: Image with 2 vertebraes and two points(labels). 
    """
    img_final = np.copy(img_seg)
    img_final[img_final > 0 ] = 0

    for i in range(len(label)):
        ref = ref_coord(label_img[i],volume[i])
        img_final[ref[1],ref[0],volume[i]] = label[i]

    img_final = np.transpose(img_final,[2,0,1])
    img_final = np.fliplr(img_final)
    
    return img_final
