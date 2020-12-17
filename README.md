# SFM for 3D root model reconstruction

The software package was integrated as a module at PlantIT website at : https://portnoy.cyverse.org/.
(Collaborate with Cyverse https://www.cyverse.org/ ) . Users are welcomed to registered as an user to try this package via PlantIT website. 

The software package was also available at Dockerhub (https://hub.docker.com/r/computationalplantscience/3d-model-reconstruction) for advanced users to run locally via singularity at Linux environment: 


Steps to run this package in container locally:
 
1. Install singularity container version 3.6 following the instruction at https://sylabs.io/guides/3.6/user-guide/quick_start.html#quick-installation-steps

2. Run the container:

   Once singularity was successfully installed, the container can be executed using 

   singularity exec --home  $PWD/  –bind  /$PWD:/opt/code/vsfm/bin/temp,/$PWD:/opt/code/vsfm/bin/log docker://computationalplantscience 
   /3d-model-reconstruction /opt/code/vsfm/bin/VisualSFM  sfm+pmvs  /$PATH_TO_IMAGE_FOLDER/

  "$PWD" : can be replaced by user’s local path for store temporary files.

  $PATH_TO_IMAGE_FOLDER/:  can be replaced by user’s image data folder. 

3. Collect the 3D model result
   After the container was executed successfully with image data files, user should be able to see output at command window like this:

  '''
  Save to /$PATH_TO_IMAGE_FOLDER/vsfm.nvm ... done
  Save /$PATH_TO_IMAGE_FOLDER/vsfm.0.ply ...done

  VisualSFM 3D reconstruction, finished
  Totally 15.000 seconds used

  LogFile: /opt/code/vsfm/bin/log/[20_12_17][15_26_12][690].log
  '''

  The 3D model was stored as point cloud in ply format at /$PATH_TO_IMAGE_FOLDER/vsfm.0.ply.



## Author
suxing liu(suxingliu@gmail.com)
reference:
[Anders Damsgaard](mailto:adamsgaard@ucsd.edu) with contributions by Caleb Adams
and Connor P Doherty.
Changchang Wu ( wucc1130@gmail.com )

Singularity container was maintained by Wesley Paul Bonelli. it was deployed to Plant IT website by Wesley Paul Bonelli (wbonelli@uga.edu).

Singularity container overlay issues were solved by [Saravanaraj Ayyampalayam] (https://github.com/raj76) (mailto:raj76@uga.edu)

Special thanks to Chris Cotter building the container recipe for testing and debugging.

## Todo
- VisualSFM is built without CUDA acceleration. Add optional GPU build.
- support GPU based SIFT feature matching

## License
GNU Public License
