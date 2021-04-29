"""
Version: 1.0

Summary: pipeline of colmap and visualSFM for 3D model reconstruction from images

Author: suxing liu

Author-email: suxingliu@gmail.com

USAGE:

python3 colmap_pipeline.py 


argument:
("-p", "--path", required = True,    help = "path to image file")


Note:
GPU related parameters
--SiftExtraction.use_gpu 
--SiftMatching.use_gpu

"""

import subprocess, os
import sys

import argparse
import glob
import fnmatch
import os, os.path


def execute_script(command):
    
    try:
        print(command)
        print()
        subprocess.run(command, shell = True)
        
    except OSError:
        
        print("Failed ...!\n")

    

def colmap_vsfm_pipeline(file_path):
    
    currentDirectory = os.getcwd()
    print(currentDirectory)
    
    if os.path.exists(file_path):
        print("Image files path exist...\n")
    else:
        print("Image files path was not valid!\n")

    feature_extract = "colmap feature_extractor --image_path " + file_path + " --database_path " + file_path + "/database.db " + "--SiftExtraction.use_gpu=false"
    execute_script(feature_extract)
    
    feature_matching = "colmap exhaustive_matcher --database_path " + file_path + "/database.db" + " --SiftMatching.use_gpu=false"
    execute_script(feature_matching)
    
    create_folder_sparse = "mkdir " + file_path + "/sparse" 
    execute_script(create_folder_sparse)
    
    sparse_model = "colmap mapper --database_path " + file_path + "/database.db " + "--image_path " + file_path + " --output_path " + file_path + "/sparse" 
    execute_script(sparse_model)
    
    nvm_model = "colmap model_converter --input_path " + file_path + "/sparse/0 " + " --output_path " + file_path + "/model.nvm " + " --output_type NVM"
    execute_script(nvm_model)
    
    dense_model = "/opt/code/vsfm/bin/VisualSFM sfm+loadnvm+pmvs " + file_path + "/model.nvm " + file_path + "/dense.nvm "
    execute_script(dense_model)
    
    
    '''
    #reserved for future GPU version
    create_folder_dense = "mkdir " + file_path + "/dense" 
    execute_script(create_folder_dense)
    
    #GPU required
    dense_model = "colmap image_undistorter --image_path "+ file_path + " --input_path " + file_path + "/sparse/0 --output_path " + file_path + "/dense --output_type COLMAP --max_image_size 2000"
    execute_script(dense_model)
    
    
    patch_match_stereo = "colmap patch_match_stereo --workspace_path " + file_path + "/dense" + " --workspace_format COLMAP --PatchMatchStereo.geom_consistency true"
    execute_script(patch_match_stereo)
    
    stereo_fusion = "colmap stereo_fusion --workspace_path " + file_path + "/dense" + " --workspace_format COLMAP --input_type geometric --output_path " + file_path + "/dense/fused.ply"
    execute_script(stereo_fusion)
    
    poisson_mesher = " colmap poisson_mesher --input_path " + file_path + "/dense/fused.ply" + " --output_path " + file_path +"/dense/meshed-poisson.ply"
    execute_script(poisson_mesher)
    '''
    
    

if __name__ == '__main__':

    # construct the argument and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--path", required = False, default = '/srv/images', help = "path to image file")
    args = vars(ap.parse_args())

   
    # setting path to cross section image files
    file_path = args["path"]
    
   
    colmap_vsfm_pipeline(file_path)
    
