"""
Version: 1.5

Summary: Automatic image brightness adjustment based on gamma correction method

Author: suxing liu

Author-email: suxingliu@gmail.com

USAGE:

python3 correct_gamma.py -p /home/suxingliu/model-scan/test-image/ -ft jpg


argument:
("-p", "--path", required = True,    help="path to image file")
("-ft", "--filetype", required=True,    help="Image filetype") 

"""

#!/usr/bin/python
# Standard Libraries

import os,fnmatch
import argparse
import shutil
from os.path import join
from pathlib import Path

import cv2

import numpy as np

import glob


import multiprocessing
from multiprocessing import Pool
from contextlib import closing

import resource


# create result folder
def mkdir(path):
    # import module
    #import os
 
    # remove space at the beginning
    path=path.strip()
    # remove slash at the end
    path=path.rstrip("\\")
 
    # path exist?   # True  # False
    isExists=os.path.exists(path)
 
    # process
    if not isExists:
        # construct the path and folder
        #print path + ' folder constructed!'
        # make dir
        os.makedirs(path)
        return True
    else:
        # if exists, return 
        #print path+' path exists!'
        return False


#adjust the gamma value to increase the brightness of image
def adjust_gamma(image, gamma):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")
 
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)


#apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to perfrom image enhancement
def image_enhance(img):

    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3., tileGridSize=(8,8))

    # convert from BGR to LAB color space
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)  
    
    # split on 3 different channels
    l, a, b = cv2.split(lab)  

    # apply CLAHE to the L-channel
    l2 = clahe.apply(l)  

    # merge channels
    lab = cv2.merge((l2,a,b))  
    
    # convert from LAB to BGR
    img_enhance = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)  
    
    return img_enhance


def correct_gamma(image_file, output_path):
    # parse the file name
    path, filename = os.path.split(image_file)
    print(f"Enhancing image {str(filename)}")

    # Load the image
    image = cv2.imread(image_file)
    
    #get size of image
    img_height, img_width = image.shape[:2]
    
    # apply gamma correction and show the images
    gamma = 1.5
    gamma = gamma if gamma > 0 else 0.1
    adjusted = adjust_gamma(image, gamma=gamma)
    enhanced_image = image_enhance(adjusted)

    # save result as images for reference
    cv2.imwrite(join(output_path, Path(image_file).stem + "_gc" + Path(image_file).suffix), enhanced_image)


if __name__ == '__main__':

    # construct the argument and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--path", required = True,    help = "path to image file")
    ap.add_argument("-ft", "--filetype", required = False,  default = 'jpg',  help = "image filetype")
    args = vars(ap.parse_args())

    # setting path to model file
    file_path = args["path"]
    ext = args['filetype']

    #accquire image file list
    filetype = '*.' + ext
    image_file_path = file_path + filetype

    #accquire image file list
    imgList = sorted(glob.glob(image_file_path))

    #print((imgList))


    # make the folder to store the results
    parent_path = os.path.abspath(os.path.join(file_path, os.pardir))
    #mkpath = parent_path + '/' + str('correct_gamma')
    mkpath = file_path + '/' + str('correct_gamma')
    mkdir(mkpath)
    save_path = mkpath + '/'

    #print "results_folder: " + save_path  

    
    # get cpu number for parallel processing
    #agents = psutil.cpu_count()   
    agents = multiprocessing.cpu_count()-1
    

    print("Using {0} cores to perfrom parallel processing... \n".format(int(agents)))
    
    # Create a pool of processes. By default, one is created for each CPU in the machine.
    # extract the bouding box for each image in file list
    with closing(Pool(processes=agents)) as pool:
        args = [(img, save_path) for img in imgList]
        result = pool.imap(correct_gamma, imgList)
        pool.terminate()
    
    # monitor memory usage
    rusage_denom = 1024.0
    
    print("Memory usage: {0} MB\n".format(int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom)))
    

    

    





    

    

    
  

   
    
    




