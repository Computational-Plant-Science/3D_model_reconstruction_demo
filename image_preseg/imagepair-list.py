"""
Version: 1.0
Summary: Generate the image pairlist for SIFT matching in Structure from Motion based model reconstruction  
Author: suxing liu
Author-email: suxingliu@gmail.com

USAGE

python imagepair-list.py -p /media/suxingliu/Data/root_image_data/PennState/1031/ -nrow 360 -ncol 10 -intervalrow 4 -intervalcol 2 

"""

# import the necessary packages
import argparse
import os
import itertools


# get hte first number from string
def extract_nbr(input_str):
    if not input_str and not isinstance(input_str, str):
        return 0
    out_number = ''
    for ele in input_str:
        if (ele == '.' and '.' not in out_number) or ele.isdigit():
            out_number += ele
        elif out_number:
            break
    return float(out_number)


def splitext_(path):
    if len(path.split('.')) > 2:
        return path.split('.')[0],'.'.join(path.split('.')[-2:])
    return os.path.splitext(path)

if __name__ == '__main__':
    # construct the arguments 
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--path", required=True,    help="path to all image data file")
    ap.add_argument("-nrow", "--number_row", required=True, type = int,    help="number of images in a circle loop")
    ap.add_argument("-ncol", "--number_col", required=True, type = int,    help="number of images in a row loop")
    ap.add_argument("-intervalrow", "--pairinterval_row", required=True, type = int,    help="interval of image pairs along row")
    ap.add_argument("-intervalcol", "--pairinterval_col", required=True, type = int,    help="interval of image pairs along col")
    ap.add_argument("-s", "--savepath", required=False,    help="path to save image pair file")
    args = vars(ap.parse_args())

    # parse the arguments 
    current_path = args["path"]

    #Set save path
    if (args["savepath"] == None):
            
        save_path = current_path + 'PairList_' + str(args["pairinterval_row"]) + '_' + str(args["pairinterval_col"]) + '.txt'
        save_path_full = current_path + 'PairList_full.txt'
    else: 
            
        save_path = args["savepath"] + 'PairList_' + str(args["pairinterval_row"]) + '_' + str(args["pairinterval_col"]) + '.txt'
        save_path_full = args["savepath"] + 'PairList_full.txt'
        
    #imgList = sorted(fnmatch.filter(os.listdir(current_path), filetype))
    
    # find all image files in the path 
    List_file = [f for f in os.listdir(current_path) if f.endswith('.jpg') or f.endswith('.JPG') ]
    
    print List_file

    #files = os.listdir(current_path)
    if len(List_file) > 0:
        
        file_name, extension = splitext_(List_file[0])
            
        for index, image in enumerate(List_file):
            
            file_new_name = '{:04}'.format(index)
            
            print file_new_name
        
            os.rename(os.path.join(current_path, image), os.path.join(current_path, ''.join([str(file_new_name), extension])))
    else:
        
        print("Empty folder")
    
    
    # define the interval paramter
    if (args["pairinterval_row"] > len(List_file)) or (args["pairinterval_row"] > args["number_row"]) :
            
        pair_interval_row = len(List_file)
    else: 
            
        pair_interval_row = args["pairinterval_row"]

    if args["pairinterval_col"] > args["number_col"]:
            
        pair_interval_col = args["number_col"]
    else: 
            
        pair_interval_col = args["pairinterval_col"]


    # Generate the combination of the image file list
    CList = list(itertools.combinations(List_file,2))


    # Count the number of image pairs with user defined interval
    count = 0

    # write out the imagepair result as text file
    outfile = open(save_path, 'w')
    outfile_full = open(save_path_full, 'w')
    try:
        for elemment in CList:
                interval_row = abs(int(extract_nbr(elemment[0]) - extract_nbr(elemment[1])))
                interval_col = abs(int(extract_nbr(elemment[0])%args["number_row"]) - int(extract_nbr(elemment[1])%args["number_row"]))
                
                str_pair = ' '.join(str(item) for item in elemment)
                
                outfile_full.write("{0}\n".format(str_pair))
                
                if (interval_row < pair_interval_row) or (interval_col < pair_interval_col):        
                #if interval_row < pair_interval_row:                
                    #print ' '.join(str(item) for item in elemment)
                    count += 1
                    outfile.write("{0}\n".format(str_pair))
                    
    finally:
        outfile.close()
        outfile_full.close()


    # output the image pair list paramters
    print ("Number of image files is: {0}\n". format(len(List_file)))
    print ("Number of full image pair combination is: {0}\n". format(len(CList)))
    print ("Number of image pair combination with definded interval is: {0}\n". format(count))
    print ("Ratio of selected image pair combination is: {:.2f}%\n". format(1.0*count/len(CList)*100.0))
        
    


