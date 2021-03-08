#!/bin/bash
# pipeline of colmap and visualSFM for 3D model reconstruction from images
# /images/ are input data files inside docker container

#feature extraction
colmap feature_extractor --image_path /srv/images --database_path /srv/images/database.db --SiftExtraction.use_gpu=false

#feature mathcing
colmap exhaustive_matcher --database_path /srv/images/database.db --SiftMatching.use_gpu=false

#generate sparse model 
colmap mapper --database_path /srv/images/database.db --image_path /srv/images/ --output_path /srv/images/sparse/

#convert sparse model format
colmap model_converter --input_path /srv/images/sparse/0 --output_path /srv/images/model.nvm --output_type NVM

#load sfm to generate dense model from sparse model
/opt/code/vsfm/bin/VisualSFM sfm+loadnvm+pmvs /srv/images/model.nvm /srv/images/dense.nvm

chmod 777 -R /srv/images/
