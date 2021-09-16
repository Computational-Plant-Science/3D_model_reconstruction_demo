"""
Version: 1.5

Summary: Fast Fourier Transform (FFT) to perform blur detection in image sequences

Author: suxing liu

Author-email: suxingliu@gmail.com

USAGE:

python3 blur_detector_image.py -p /home/suxingliu/fft-blur-detector/images/ -ft jpg 


argument:
("-p", "--path", required = True,    help="path to image file")
("-ft", "--filetype", required = True,    help="Image filetype")

"""

# !/usr/bin/python
# Standard Libraries

# import the necessary packages
import os, fnmatch
import shutil
from os.path import join

import numpy as np
import glob

import multiprocessing
from multiprocessing import Pool
from contextlib import closing

import resource

from model_preprocess.blur_detector import detect_blur_fft
import numpy as np
import argparse
import imutils
import cv2


# create result folder
def mkdir(path):
    # import module
    # import os

    # remove space at the beginning
    path = path.strip()
    # remove slash at the end
    path = path.rstrip("\\")

    # path exist?   # True  # False
    isExists = os.path.exists(path)

    # process
    if not isExists:
        # construct the path and folder
        # print path + ' folder constructed!'
        # make dir
        os.makedirs(path)
        return True
    else:
        # if exists, return 
        # print path+' path exists!'
        return False


def detect_blur(image_path, output_path):
    # parse the file name
    path, filename = os.path.split(image_path)

    print(f"Running blur detection for {str(filename)}")

    # load the input image from disk, resize it, and convert it to grayscale
    orig = cv2.imread(image_path)
    if orig is None:
        print(f"Could not read image {image_path}, skipping")
        return

    orig = imutils.resize(orig, width=500)
    gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)

    # apply our blur detector using the FFT
    (mean, blurry) = detect_blur_fft(gray, size=60, thresh=20, vis=(-1 > 0))

    if blurry:
        print("Blurry")
        os.remove(join(output_path, filename))  # remove the blurry image from the output directory
        # shutil.move(image_path, join(output_path, str(filename[0:-4]) + '.' + ext))
    else:
        print("Clear")

    # return blurry


if __name__ == '__main__':
    # construct the argument and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--path", required=True, help="path to image file")
    ap.add_argument("-ft", "--filetype", required=False, default='jpg', help="image filetype")
    args = vars(ap.parse_args())

    global file_path, ext, save_path

    # setting path to model file
    file_path = args["path"]
    ext = args['filetype']

    # accquire image file list
    filetype = '*.' + ext
    image_file_path = file_path + filetype

    # accquire image file list
    imgList = sorted(glob.glob(image_file_path))

    print((imgList))

    # make the folder to store the results
    parent_path = os.path.abspath(os.path.join(file_path, os.pardir))
    mkpath = parent_path + '/' + str('blur_images')
    mkdir(mkpath)
    save_path = mkpath + '/'

    print("results_folder: " + save_path)

    # get cpu number for parallel processing
    # agents = psutil.cpu_count()
    agents = multiprocessing.cpu_count() - 1

    print("Using {0} cores to perfrom parallel processing... \n".format(int(agents)))

    # Create a pool of processes. By default, one is created for each CPU in the machine.
    # extract the bouding box for each image in file list
    with closing(Pool(processes=agents)) as pool:
        # result = pool.map(foreground_substractor, imgList)
        args = [(img, save_path) for img in imgList]
        pool.imap(detect_blur, args)
        pool.terminate()
