'''
Name: down_sample.py

Version: 1.0

Summary: Select pairs among image list
    
Author: suxing liu

Author-email: suxingliu@gmail.com

Created: 2019-09-29

USAGE:

python3 remove_image_folder.py -p ~/molly_root/


'''

# import the necessary packages
import os
import glob
import argparse
import shutil

# generate foloder to store the output results
def remove(path):
 
    # remove space at the beginning
    #path=path.strip()
    # remove slash at the end
    #path=path.rstrip("\\")
 
    # path exist?   # True  # False
    isExists=os.path.exists(path)
 
    # process
    if not isExists:
        # construct the path and folder
        #print path + ' folder constructed!'
        # make dir
        print ('path not exists!')

    else:
        # if exists, return 
        
        print ('path exists!')
        #shutil.rmtree(path)
        
    #os.makedirs(path)

        


if __name__ == '__main__':
    
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--path", required = True,    help="path to image file")
    args = vars(ap.parse_args())
    

    # setting path to model file
    file_path = args["path"]

   
    #accquire image file list
    imgList = os.listdir(file_path)
    
   # imgList = [x[0] for x in os.walk(file_path)]
    #print(glob.glob("/home/adam/*.txt")) 
    
    print(imgList)
   
    
    #loop execute
    for (i, image_file) in enumerate(imgList):

        current_path = file_path + image_file
        
        sub_imgList = os.listdir(current_path)
        
        #print(current_path)
        
        for (j, sub_path) in enumerate(sub_imgList):
            
            full_path = current_path + "/" + str(sub_path) + "/images/"
            
            print(full_path)
        
            remove(full_path)
        
            
        
        
