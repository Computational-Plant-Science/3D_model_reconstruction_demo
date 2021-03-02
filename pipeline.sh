#!/bin/bash
# pipeline of colmap and visualSFM for 3D model reconstruction from images
# /images/ are input data files inside docker container

#feature extraction
colmap feature_extractor --image_path /images/ --database_path /images/database.db --SiftExtraction.use_gpu=false

#feature mathcing
colmap exhaustive_matcher --database_path /images/database.db --SiftMatching.use_gpu=false

#generate sparse model 
mkdir /images/sparse

colmap mapper --database_path /images/database.db --image_path /images/ --output_path /images/sparse/

#convert sparse model format
colmap model_converter --input_path /images/sparse/0 --output_path /images/model.nvm --output_type NVM

#load sfm to generate dense model from sparse model
/opt/code/vsfm/bin/VisualSFM sfm+loadnvm+pmvs /images/model.nvm /images/dense.nvm

chmod 777 -R /images/
