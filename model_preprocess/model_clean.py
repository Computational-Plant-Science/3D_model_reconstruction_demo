"""
Version: 1.5

Summary: Clean 3D root model, remove outlier points based on fast mian component kmean cluster method

Author: suxing liu

Author-email: suxingliu@gmail.com

USAGE:

python3 model_clean.py -p /home/suxingliu/model-scan/model-data/ -m bean.ply -c 10 -t 3


argument:
("-p", "--path", required=True,    help="path to *.ply model file")
("-m", "--model", required=True,    help="file name")
("-c", "--number_cluster", required=True,    type = int, help="color space cluster number")
("-t", "--number_top", required=True,    type = int, help="top cluster number") 


Note:
#ply data structure
PlyData((PlyElement('vertex', (PlyProperty('x', 'float'), PlyProperty('y', 'float'), PlyProperty('z', 'float'), 

                                PlyProperty('nx', 'float'), PlyProperty('ny', 'float'), PlyProperty('nz', 'float'), 
                                
                                PlyProperty('diffuse_red', 'uchar'), PlyProperty('diffuse_green', 'uchar'), PlyProperty('diffuse_blue', 'uchar'), 
                                
                                PlyProperty('psz', 'float')), 
                                
                                count=1193077, comments=[]),), text=False, byte_order='<', comments=[], obj_info=[])
"""


# import the necessary packages
from __future__ import print_function

from plyfile import PlyData, PlyElement

import numpy as np
import argparse
import pandas as pd

from sklearn import preprocessing

from scipy.spatial import cKDTree
from scipy import argmax

# save figure without display
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import colors

from mpl_toolkits.mplot3d import Axes3D

from pyspark import SparkContext
from pyspark.ml.clustering import KMeans
from pyspark.ml.feature import VectorAssembler
from pyspark.sql import SQLContext

import os
os.environ["PYSPARK_PYTHON"]="/usr/bin/python3"



def find_histogram(dfList, centers, n_top):
    """
    create a histogram with k clusters
    :param: clt
    :return:hist
    """
    #compute the number of bins
    numLabels = np.arange(0, len(np.unique(dfList)) + 1)
    hist, bins = np.histogram(dfList, bins = numLabels)
    
    # normalize the histogram, such that it sums to one
    hist = hist.astype("float")
    hist /= hist.sum()
    
    width = 0.7 * (bins[1] - bins[0])
    center = (bins[:-1] + bins[1:]) / 2
    
    # show the histogram
    fig = plt.figure()
    
    barlist = plt.bar(center, hist, align = 'center', width = width)
    
    for index, center in enumerate(centers):
        #print(index, center)
        color = center/255.0
        barlist[index].set_color(color)
    
    #plt.show()
    plt.savefig('hist.png')
    plt.close(fig)
    
    # find most frequent
    #index_max = argmax(hist)
    
    #find the top n among frequency 
    index_top = hist.argsort()[::-1][:n_top]
    
    #peak = dfList[index_max]
       
    #print(dfList[argmax(hist)])

    return index_top

def colorspace_show(extracted_data):

    # visualization of the data
    fig = plt.figure()
    axis = fig.add_subplot(1, 1, 1, projection = "3d")
    pixel_colors = extracted_data
    norm = colors.Normalize(vmin=-1.,vmax=1.)
    norm.autoscale(pixel_colors)
    pixel_colors = norm(pixel_colors).tolist()
    
    # show rgb colorspace 
    axis.scatter(extracted_data[:,0].flatten(), extracted_data[:,1].flatten(), extracted_data[:,2].flatten(), facecolors = pixel_colors, marker=".")
    axis.set_xlabel("Red")
    axis.set_ylabel("Green")
    axis.set_zlabel("Blue")
    plt.show()
    plt.savefig('color_distributation.png')
    plt.close(fig)

#machine learing based spark kmeans method, arguments: data & number of cluster
def spark_kmeans(extracted_data, n_cluster):
    
    # convert data to float type for spark data frame
    extracted_data = np.array(extracted_data, dtype = float)
    
    #extracted_data = rgb2lab(extracted_data)
    
    FEATURES_COL = ['r', 'g', 'b']
    
    pddf = pd.DataFrame(extracted_data, columns = FEATURES_COL)

    #add a row index as a string
    pddf['id'] = pddf.index.astype(str)
    
    #fill the digits in ID row 
    pddf['id'] = pddf['id'].apply(lambda x: x.zfill(len(str(len(extracted_data)))))

    #move it first (left)
    cols = list(pddf)
    cols.insert(0, cols.pop(cols.index('id')))
    pddf = pddf.loc[:, cols]
    
    #initialize sparkcontext dataframe 
    sc = SparkContext(appName = "Spark_KMeansApp")
    
    #Read in data from CSV into a Spark data frame
    sqlContext = SQLContext(sc)
    
    #convert datatype from pandas dataframe to spark dataframe
    df = sqlContext.createDataFrame(pddf)
    
    df.show()
    
    #Create a features column to be used in the clustering
    vecAssembler = VectorAssembler(inputCols = FEATURES_COL, outputCol = "features")
    
    # spark data frame for kmeans clustering 
    df_kmeans = vecAssembler.transform(df).select('id', 'features')
    
    #Train the machine learning model
    kmeans = KMeans().setK(n_cluster).setSeed(1).setFeaturesCol("features")
    model = kmeans.fit(df_kmeans)
    centers = model.clusterCenters()

    print("Cluster Centers: ")
    for center in centers:
        print(center)
        
     #Assign clusters to events
    transformed = model.transform(df_kmeans).select('id', 'prediction')
    rows = transformed.collect()

    #extract predicted data
    df_pred = sqlContext.createDataFrame(rows)

    #Join the prediction with the original data
    df_pred = df_pred.join(df, 'id')

    # sort the data by id value
    df_pred = df_pred.orderBy("id")
    
    print("clustered data:")
    df_pred.show()
    
       
    #extract predict values
    pddf_pred = df_pred.toPandas().set_index('id')
    dfList = pddf_pred['prediction'].values
    
    #close sc content
    sc.stop()
    
    print(dfList)
    
    return dfList, centers
    

    
if __name__ == '__main__':
    
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--path", required=True,    help="path to *.ply model file")
    ap.add_argument("-m", "--model", required=True,    help="file name")
    ap.add_argument("-c", "--number_cluster", required=True,    type = int, help="color space cluster number")
    ap.add_argument("-t", "--number_top", required=True,    type = int, help="top cluster number")
    args = vars(ap.parse_args())

        
    # setting path to model file 
    current_path = args["path"]
    filename = args["model"]
    file_path = current_path + filename
    save_path = current_path + 'Cleaned_' +filename


    # load the model file
    with open(file_path, 'rb') as f:
        plydata = PlyData.read(f)
        num_vertex = plydata.elements[0].count
        
        print("Load ply model file {0}: \n".format(filename))
        print("Ply data structure: \n")
        print(plydata)
        print("Number of 3D points in current model is: {0} \n".format(num_vertex))
    
    
    #Parse the ply format file and Extract the data
    Data_array = np.zeros((num_vertex, len(plydata.elements[0].properties)))

    #Extract property list
    for index, item in enumerate(plydata.elements[0].properties, start = 0):
        Data_array[:,index] = plydata['vertex'].data[item.name]

    
    #extract colosr space data for clustering  
    extracted_data = Data_array[:,[6,7,8]]
    
    # visualize the colorspace
    #colorspace_show(extracted_data)
    
    
    
    #define number of cluster, can be optimized based on cost
    n_cluster = args["number_cluster"]
    
    #define top number of clusters to be removed
    n_top = args["number_top"]
    
    # saprk kmeans method for colorspace clustering 
    (dfList, centers) = spark_kmeans(extracted_data, n_cluster)
    
    index_top = find_histogram(np.array(dfList), centers, n_top)
    
    #print(type(dfList))
    #print("peak group is {0} \n:".format(str(index_top)))
    
    #combine all top clusters
    if (n_top == 1):
        condition = (dfList == index_top)
    else:
        for i in range(0, n_top-1):
            condition = ((dfList == index_top[i]) | (dfList == index_top[i+1]))
        
    #print(condition)
    
    
    Index_array = np.column_stack(np.where(condition))
    
    #print(Index_array)
    
    #Remove 3d points 
    Data_clean = np.delete(Data_array, np.where(condition)[0], 0)

    percent = 100*(np.count_nonzero(Index_array))/num_vertex
    print("Percentage of removed points: {0} %\n".format(percent))

    #print(Data_clean)
    #print(Data_clean.shape)
    print("Number of new 3D points in updated model is: {0} \n".format(len(Data_clean)))


    #Extract property list
    property_list = list(plydata.elements[0].properties)

    for index, item in enumerate(plydata.elements[0].properties, start = 0):
        property_list[index] = (item.name,item.val_dtype)

    #Assign datatype
    mydtype = property_list

    #Converting a 2D numpy array to a structured array             
    Data_structured_array = np.core.records.array(list(tuple(Data_clean.transpose())), dtype = mydtype)

    #print(Data_structured_array)
    #print (type(Data_structured_array))

    #Create the ply object instances
    ply_struct_instance = PlyElement.describe(Data_structured_array, 'vertex', comments=[])


    #Save cleaned ply model file
    #save_file_name = current_path + 'Cleaned_T' + str(int(Thresh)) + '_' + filename
    save_file_name = current_path + 'cleaned_' + filename
    PlyData([ply_struct_instance], text = False).write(save_file_name)




