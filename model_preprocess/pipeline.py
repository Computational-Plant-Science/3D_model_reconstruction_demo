"""
Version: 1.5

Summary: image pre-processingfor 3D model reconstruction 

Author: suxing liu

Author-email: suxingliu@gmail.com

USAGE:

python pipeline.py -p /path_to_image_folder/ -ft jpg

parameter list:

argument:
("-p", "--path", required = True,    help = "path to image file")
("-ft", "--filetype", required = True,    help = "Image filetype")


"""

import subprocess, os
import sys
import argparse
#import glob

def execute_script(cmd_line):
    """execute script inside program"""
    try:
        print(cmd_line)
        #os.system(cmd_line)
        
        process = subprocess.Popen(cmd_line, shell = True, stdout = subprocess.PIPE)
        
        process.wait()
        
        #print process.returncode
        
    except OSError:
        
        print("Failed ...!\n")


def image_prepocess(current_path):
    """execute pipeline scripts"""
    
    #/opt/code/bbox_seg.py -p /home/suxingliu/frame-interpolation/test-image/ -ft jpg
    
    # step1 : Region of Interest extraction
    ROI_seg = "python /opt/code/bbox_seg.py -p " + current_path + " -ft " + str(ext)
    
    print("Extracting Region of Interest from input images...\n")
    
    execute_script(ROI_seg)
    
    #change the path to parent folder
    parent_path = os.path.abspath(os.path.join(current_path, os.pardir))
    #mkpath = parent_path + '/' + str('segmented')
    
    # step2 : correct_gamma
    gamma_correction = "python /opt/code/correct_gamma.py -p " + parent_path + "/segmented/"
    
    print("Luminance enhancement by correct_gamma method...\n")
    
    execute_script(gamma_correction)
    


if __name__ == '__main__':
    
    # construct the argument and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--path", required = True,    help = "path to image file")
    ap.add_argument("-ft", "--filetype", required = False,  default = 'jpg', help = "image filetype")
    args = vars(ap.parse_args())
    
    
    # setting path to model file
    file_path = args["path"]
    ext = args['filetype']

    # accquire image file list
    #filetype = '*.' + ext
    #image_file_path = file_path + filetype

    #accquire image file list
    #imgList = sorted(glob.glob(file_path + filetype))

    #print((imgList))

    # execute the main pipeline
    image_prepocess(file_path)
    
    
