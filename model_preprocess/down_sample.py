'''
Name: down_sample.py

Version: 1.0

Summary: Select pairs among image list
    
Author: suxing liu

Author-email: suxingliu@gmail.com

Created: 2019-09-29

USAGE:

python3 down_sample.py -p ~/example/ -ft jpg -r 10

python3 down_sample.py -p /media/suxing/DATA/root_image_data/Molly_roots/DKPB80X3IIH6/DKPB80X3IIH6-1/ -ft jpg -r 4

python3 down_sample.py -p ~/molly_root/H96X3IIH6/H96X3IIH6-1/ -ft jpg -r 5


'''

# import the necessary packages
import os
import glob
import argparse
import shutil

# generate foloder to store the output results
def mkdir(path):
    # import module
    import os
 
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
        shutil.rmtree(path)
        print ('path exists!')
        os.makedirs(path)
        return True
        


if __name__ == '__main__':
    
    ap = argparse.ArgumentParser()
    #ap.add_argument('-i', '--image', required = True, help = 'Path to image file')
    ap.add_argument("-p", "--path", required = True,    help="path to image file")
    ap.add_argument("-ft", "--filetype", required = True,    help="Image filetype")
    ap.add_argument("-r", "--ratio", required = True, type = int, help="Downsample ratio")
    args = vars(ap.parse_args())
    

    # setting path to model file
    file_path = args["path"]
    ext = args['filetype']
    ratio = int(args['ratio'])
    
    # make the folder to store the results
    # save folder construction
    mkpath = os.path.dirname(file_path) +'/images'
    mkdir(mkpath)
    save_path = mkpath + '/'
    print("results_folder: {0}\n".format(str(save_path)))  
    
    #accquire image file list
    filetype = '*.' + ext
    image_file_path = file_path + filetype
    
    #accquire image file list
    imgList = (glob.glob(image_file_path))
    
    #print(glob.glob("/home/adam/*.txt")) 
    
    #print(imgList)
    
     
    #loop execute
    for (i, image_file) in enumerate(imgList):

        filename, file_extension = os.path.splitext(image_file)
    
        base_name = os.path.splitext(os.path.basename(filename))[0]
        
        #print(image_file)
        
        dst = (save_path + base_name + '.' + ext)
        
       
        if i % ratio == 0:
        
            shutil.copy(image_file, dst)
            
        
        
