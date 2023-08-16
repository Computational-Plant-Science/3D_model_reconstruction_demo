"""
Version: 1.5

Summary: ConvelHull based bounding box segmenation for image sequence

Author: suxing liu

Author-email: suxingliu@gmail.com

USAGE:

python3 bbox_seg_mask.py -p ~/example/test/ -ft jpg 


argument:
("-p", "--path", required = True,    help="path to image file")
("-ft", "--filetype", required = True,    help="Image filetype")

"""

#!/usr/bin/python
# Standard Libraries

import os,fnmatch
import argparse
import shutil
import cv2

import numpy as np
#import matplotlib.pyplot as plt

import glob
from math import atan2, cos, sin, sqrt, pi, radians

import multiprocessing
from multiprocessing import Pool
from contextlib import closing

import cv2
#import psutil

import resource
import os

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


def get_orientation(pts):
    
    sz = len(pts)
    data_pts = np.empty((sz, 2), dtype=np.float64)
    for i in range(data_pts.shape[0]):
        data_pts[i,0] = pts[i,0,0]
        data_pts[i,1] = pts[i,0,1]
    # Perform PCA analysis
    mean = np.empty((0))
    mean, eigenvectors, eigenvalues = cv2.PCACompute2(data_pts, mean)
    # Store the center of the object
    cntr = (int(mean[0,0]), int(mean[0,1]))
    
    '''
    cv2.circle(img, cntr, 3, (255, 0, 255), 2)
    p1 = (cntr[0] + 0.02 * eigenvectors[0,0] * eigenvalues[0,0], cntr[1] + 0.02 * eigenvectors[0,1] * eigenvalues[0,0])
    p2 = (cntr[0] - 0.02 * eigenvectors[1,0] * eigenvalues[1,0], cntr[1] - 0.02 * eigenvectors[1,1] * eigenvalues[1,0])
    draw_axis(img, cntr, p1, (0, 150, 0), 1)
    draw_axis(img, cntr, p2, (200, 150, 0), 5)
    '''
    
    angle = atan2(eigenvectors[0,1], eigenvectors[0,0]) # orientation in radians
    
    print("orientation in radians is {}".format(angle*180/pi))
    
    return angle


def slope(x1, y1, x2, y2):
    if x1 == x2:
        return 0
    slope = (y2-y1)/(x2-x1)
    theta = np.rad2deg(np.arctan(slope))
    return theta


def createMask(rows, cols, hull, value):
    
    # black image
    mask = np.zeros((rows, cols), dtype=np.uint8)
    
    # assign contours in white color
    cv2.drawContours(mask, [hull], 0, 255, -1)
    
    return mask
    

def foreground_substractor(image_file):
    
  
    #parse the file name 
    path, filename = os.path.split(image_file)
    
    # construct the result file path
    #result_img_path = save_path + str(filename[0:-4]) + '_seg.png'
    
    print("Extracting foreground for image : {0} \n".format(str(filename)))
    
    # Load the image
    image = cv2.imread(image_file)
    
    if image is None:
        print(f"Could not load image {image_file}, skipping")
        return
    
    
    ori = image.copy()
    
    #get size of image
    img_height, img_width = image.shape[:2]
    
    #scale_factor = 1
    
    #image = cv2.resize(image, (0,0), fx = scale_factor, fy = scale_factor) 
    
    # Convert BGR to GRAY
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    blur = cv2.blur(gray, (3, 3)) # blur the image
    #blur = cv2.GaussianBlur(gray, (25, 25), 0)
    
    #Obtain the threshold image using OTSU adaptive filter
    ret, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    #thresh = cv2.erode(thresh, None, iterations=2)
    
    #thresh = cv2.dilate(thresh, None, iterations=2)
 

            
    # extract the contour of subject
    #im, cnts, hier = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    cnts, hier = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #find the max contour 
    c = max(cnts, key = cv2.contourArea)
    

    mask_contour = createMask(img_height, img_width, c, 0)
    
    masked_fg_contour = cv2.bitwise_and(image, image, mask = mask_contour)
    
    
    linewidth = 10
    
    hull = cv2.convexHull(c)
    
    mask_hull = createMask(img_height, img_width, hull, 0)
    
    kernel = np.ones((10,10), np.uint8)
    
    mask_hull_dilation = cv2.dilate(mask_hull, kernel, iterations=1)
    
    # apply individual object mask
    masked_fg = cv2.bitwise_and(image, image, mask = mask_hull_dilation)
    
    masked_bk = cv2.bitwise_and(image, image, mask = ~ mask_hull_dilation)
    
    masked_bk_gray = cv2.cvtColor(masked_bk, cv2.COLOR_BGR2GRAY)
    
    avg_color_per_row = np.average(masked_bk_gray, axis=0)
    
    avg_color = int(np.average(avg_color_per_row, axis=0))
    
    '''
    max_contour = c
    
    #get_orientation(max_contour)
    
    rect = cv2.minAreaRect(max_contour)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    orientation = slope(box[0][0], box[0][1], box[1][0], box[1][1])
    
    #draw bounding box
    cv2.drawContours(masked_fg_contour, [box],0,(0,0,255),5)

    print("Image orientation in degress: ", orientation)
    
    M = cv2.moments(max_contour)

    if M["m00"] > 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

    #fit elipse
    ellipse = cv2.fitEllipse(max_contour)
    (xc,yc),(d1,d2),angle = ellipse
    P1x = cX
    P1y = cY
    length = 350

    #calculate vector line at angle of bounding box
    P2x = int(P1x + length * cos(radians(angle)))
    P2y = int(P1y + length * sin(radians(angle)))
     #draw vector line
    cv2.line(masked_fg_contour,(cX, cY),(P2x,P2y),(0,0,255),5)
    
    cv2.ellipse(masked_fg_contour, ellipse, (0, 255, 0), 3)
    # draw circle at center
    xc, yc = ellipse[0]
    cv2.circle(masked_fg_contour, (int(xc),int(yc)), 10, (255, 255, 255), -1)

    # draw vertical line
    # compute major radius
    rmajor = max(d1,d2)/2
    if angle > 90:
        angle = angle - 90
    else:
        angle = angle + 90
    print(angle)
    xtop = xc + cos(radians(angle))*rmajor
    ytop = yc + sin(radians(angle))*rmajor
    xbot = xc + cos(radians(angle+180))*rmajor
    ybot = yc + sin(radians(angle+180))*rmajor
    cv2.line(masked_fg_contour, (int(xtop),int(ytop)), (int(xbot),int(ybot)), (0, 0, 255), 3)

    '''
    
    
    #print(avg_color)
    
    # black image
    #mask_hull_avg = np.full((img_height, img_width), avg_color, dtype=np.uint8)
    
    # assign contours in white color
    #cv2.drawContours(mask_hull_avg, [hull], 0, 255, -1)
    
    #masked_bk_avg = cv2.bitwise_and(mask_hull_avg, mask_hull_avg, mask = ~ mask_hull_dilation)
    
    
    # replace background color with average color value
    # load background (could be an image too)
    bk = np.full(image.shape, avg_color, dtype=np.uint8)
    
    # get masked foreground
    
    fg_masked = cv2.bitwise_and(image, image, mask=mask_hull_dilation)
    
    # get masked background, mask must be inverted
    
    bk_masked = cv2.bitwise_and(bk, bk, mask=cv2.bitwise_not(mask_hull_dilation))
    
    # combine masked foreground and masked background
    combined_fg_bk = cv2.bitwise_or(fg_masked, bk_masked)
    
    '''
    # draw it in red color
    trait_img = cv2.drawContours(image, [hull], -1, (0, 0, 255), linewidth)
    
    # draw the outline of the object, then draw each of the
    # extreme points, where the left-most is red, right-most
    # is green, top-most is blue, and bottom-most is teal
    trait_img = cv2.drawContours(image, [c], -1, (0, 255, 255), linewidth)
    
    # determine the most extreme points along the contour
    extLeft = tuple(c[c[:,:,0].argmin()][0])
    extRight = tuple(c[c[:,:,0].argmax()][0])
    extTop = tuple(c[c[:,:,1].argmin()][0])
    extBot = tuple(c[c[:,:,1].argmax()][0])

    trait_img = cv2.circle(image, extLeft, linewidth, (255, 0, 0), -1)
    trait_img = cv2.circle(image, extRight, linewidth, (255, 0, 0), -1)
    trait_img = cv2.circle(image, extTop, linewidth, (255, 0, 0), -1)
    trait_img = cv2.circle(image, extBot, linewidth, (255, 0, 0), -1)

    from scipy.spatial import distance as dist
    
    max_width = dist.euclidean(extLeft, extRight)
    max_height = dist.euclidean(extTop, extBot)

    trait_img = cv2.line(image, extLeft, extRight, (0,255,0), linewidth)
    trait_img = cv2.line(image, extTop, extBot, (0,255,0), linewidth)
    
    # construct the result file path
    result_img_path = save_path + str(filename[0:-4]) + '_seg.' + ext
    
    cv2.imwrite(result_img_path, trait_img)
    '''
    ##############################################################
    
    # find the bouding box of the max contour
    (x, y, w, h) = cv2.boundingRect(c)

    # draw the max bounding box
    #cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # construct the result file path
    #result_img_path = save_path + str(filename[0:-4]) + '_seg.' + ext
    
    # save result as images for reference
    #cv2.imwrite(result_img_path,image)
    
    #print(int(x/scale_factor),int(y/scale_factor),int(w/scale_factor),int(h/scale_factor))
    
    #return int(x/scale_factor),int(y/scale_factor),int(w/scale_factor),int(h/scale_factor), int(img_width), int(img_height)
    

    
    
    margin = 150
    
    # define crop region
    start_y = int((y - margin) if (y - margin )> 0 else 0)
    
    start_x = int((x - margin) if (x - margin )> 0 else 0)
    
    crop_width = int((x + margin + w) if (x + margin + w) < img_width else (img_width))
    
    crop_height = int((y + margin + h) if (y + margin + h) < img_height else (img_height))
    
    #print img_width , img_height 
    
    # construct the result file path
    result_img_path = save_path + str(filename[0:-4]) + '_seg.' + ext
    
    #crop_img = combined_fg_bk[start_y:crop_height, start_x:crop_width]
    
    #crop_img = masked_fg_contour[start_y:crop_height, start_x:crop_width]
    
    if args['bounding_box'] == 1:
        crop_img = ori[start_y:crop_height, start_x:crop_width]
    else:
        #crop_img = combined_fg_bk[start_y:crop_height, start_x:crop_width]
        crop_img = masked_fg_contour[start_y:crop_height, start_x:crop_width]
        
    cv2.imwrite(result_img_path, crop_img)
    
    
    #return int(x),int(y),int(w),int(h), int(img_width), int(img_height)

'''
##opencv crop image function, failed when file numer exceed 1250
def crop_image(image_file):
    
    #parse the file name 
    path, filename = os.path.split(image_file)
    
    print("Saving cropped image : {0} \n".format(str(filename)))
    
    # construct the result file path
    result_img_path = save_path + str(filename[0:-4]) + '_seg.' + ext
    
    margin = 150
    
    #Load the image
    img = cv2.imread(image_file)
    
    crop_img = img[(y-margin):(y + margin + height), (x -margin):(x + margin + width)]
    
    cv2.imwrite(result_img_path,crop_img)
    



def crop_pil(image_file):
    
    #Load the image
    img = Image.open(image_file)
    
    #parse the file name
    path, filename = os.path.split(image_file)
    
    print("Saving cropped image : {0} \n".format(str(filename)))
    
    # construct the result file path
    result_img_path = save_path + str(filename[0:-4]) + '_seg.' + ext
    
    # define crop image region margin 
    margin = 100
    
    # define crop region
    start_x = (y - margin) if (y - margin )> 0 else 0
    
    start_y = (x - margin) if (x - margin )> 0 else 0
    
    crop_width = (height + 2*margin) if (start_x + height + 2*margin) < img_height else (start_x + height + 2*margin - img_height)
    
    crop_height = (width + 2*margin) if (start_y + width + 2*margin) < img_width else (start_y + width + 2*margin - img_width)
    
    # perfrom crop action
    crop_img = img.crop((start_x, start_y, crop_width, crop_height))
    
    # save result by writing image out
    crop_img.save(result_img_path)

'''



if __name__ == '__main__':

    # construct the argument and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--path", required = True,    help = "path to image file")
    ap.add_argument("-ft", "--filetype", required = False,  default = 'jpg' ,    help = "image filetype")
    ap.add_argument("-b", "--bounding_box", required = False,  type = int, default = 0, help = "using bounding box")
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
    mkpath = file_path + '/' + str('segmented')
    mkdir(mkpath)
    save_path = mkpath + '/'

    print ("results_folder: " + save_path)

    
    # get cpu number for parallel processing
    #agents = psutil.cpu_count()   
    agents = multiprocessing.cpu_count()-1
    
    
    print("Using {0} cores to perfrom parallel processing... \n".format(int(agents)))
    
    # Create a pool of processes. By default, one is created for each CPU in the machine.
    # extract the bouding box for each image in file list
    with closing(Pool(processes = agents)) as pool:
        #result = pool.map(foreground_substractor, imgList)
        pool.map(foreground_substractor, imgList)
        pool.terminate()
    
    
    
    '''
    for image_file in imgList:
        foreground_substractor(image_file)
        
    
    
    # parse the result 
    x = min(list(zip(*result)[0]))
    
    y = min(list(zip(*result)[1]))
    
    width = max(list(zip(*result)[2]))
    
    height = max(list(zip(*result)[3]))
    
    img_width = min(list(zip(*result)[4]))
    
    img_height = min(list(zip(*result)[5]))
    
    print("Coordinates of max bounding box: {0} , {1} \n".format(int(x),int(y)))
    
    print("Dimension of max bounding box: {0} , {1} \n".format(int(width),int(height)))
    
    print("Image size: {0} , {1} \n".format(int(img_width),int(img_height)))
    
    
    
    # perfrom crop action based on bouding box results in parallel way
    with closing(Pool(processes = agents)) as pool:
        #pool.map(crop_pil, imgList)
        pool.map(crop_image, imgList)
        pool.terminate()
    

    # monitor memory usage 
    rusage_denom = 1024.0
    
    print("Memory usage: {0} MB\n".format(int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom)))
    '''
    
    
    '''
    #rename all the images in soting order
    ######################################################
     # setting path to result file
    ori_path = current_path
    dst_path = save_path

     #accquire image file list
    imgList_ori = sorted(fnmatch.filter(os.listdir(ori_path), filetype))
    imgList_dst = sorted(fnmatch.filter(os.listdir(dst_path), filetype))

    imgList = sorted(imgList_ori + imgList_dst)

    # make the folder to store the results
    mkpath = current_path + str('interpolation_result')
    mkdir(mkpath)
    save_path = mkpath + '/'

    #Combine the interpolation result with original images and rename all the results
    file_sort(imgList)
    
    #delete the interpolation result folder
    try:
        shutil.rmtree(dst_path, ignore_errors=True)
        
        print "Phase based motion frame prediction and interpolation was finished!\n"
        
        print "results_folder: " + save_path  
        
    except OSError:
        pass

    '''



 

    

    

    
  

   
    
    



