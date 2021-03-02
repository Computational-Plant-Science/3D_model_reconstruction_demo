# 3D root model reconstruction

The software package was integrated as a module at PlantIT website at : https://portnoy.cyverse.org/.
(Collaborate with Cyverse https://www.cyverse.org/ ) . Users are welcomed to registered as an user to try this package via PlantIT website. 

The software package was also available at Dockerhub (https://hub.docker.com/r/computationalplantscience/3d-model-reconstruction) for advanced users to run locally via singularity at Linux environment: 

This software can be run by docker container, users do not need to install many libraries and compile complex source files. 
 
# Setup Docker container
########################################################################
1. OS requirements

    To install Docker container (https://docs.docker.com/engine/install/ubuntu/): 

    To install Docker Engine, you need the 64-bit version of one of these Ubuntu versions:

    Ubuntu Groovy 20.10
    Ubuntu Focal 20.04 (LTS)
    Ubuntu Bionic 18.04 (LTS)
    Ubuntu Xenial 16.04 (LTS)

    Docker Engine is supported on x86_64 (or amd64), armhf, and arm64 architectures.

    Uninstall old versions
    $ sudo apt-get remove docker docker-engine docker.io containerd runc

    Set up the repository

    Update the apt package index and install packages to allow apt to use a repository over HTTPS:

    $ sudo apt-get update

    $ sudo apt-get install \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg-agent \
        software-properties-common

    Add Docker’s official GPG key:

    $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

    Verify that you now have the key with the fingerprint 9DC8 5822 9FC7 DD38 854A  E2D8 8D81 803C 0EBF CD88, by searching for the last 8 characters of the fingerprint.

    $ sudo apt-key fingerprint 0EBFCD88

    pub   rsa4096 2017-02-22 [SCEA]
          9DC8 5822 9FC7 DD38 854A  E2D8 8D81 803C 0EBF CD88
    uid           [ unknown] Docker Release (CE deb) <docker@docker.com>
    sub   rsa4096 2017-02-22 [S]

    $ sudo add-apt-repository \
       "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
       $(lsb_release -cs) \
       stable"

    Update the apt package index, and install the latest version of Docker Engine and containerd, or go to the next step to install a specific version:

    $ sudo apt-get update
    $ sudo apt-get install docker-ce docker-ce-cli containerd.io

    Verify that Docker Engine is installed correctly by running the hello-world image.

    $ sudo docker run hello-world
    

########################################################################
Steps to run this container by building it locally:
 
2. Run the container:

   # Clone source code to your local path
   $ git clone https://github.com/Computational-Plant-Science/3D_model_reconstruction_demo.git
   
   # Enter into the source code folder named as "cd 3D_model_reconstruction_demo"
   $ cd 3D_model_reconstruction_demo/
   
   # Build docker container locally named as "3d_model_reconstruction" using "Dockerfile" in the same folder, note: docker repository name must be lowercase.
   $ docker build -t 3d_model_reconstruction -f Dockerfile .
   
   # Run the docker container by linking docker container data path to user's image data folder local path
   # Note: please replace $path_to_image_folder as your local image data folder path, 
   # Suggest to check your image folder path using "pwd" command
   # Example: $ docker run -v /home/suxing/example/root_images:/images -it 3d_model_reconstruction
   
   $ docker run -v /$path_to_image_folder:/images -it 3d_model_reconstruction
   
   # After launch the docker container, run "pipeline.sh" or "pipeline.sh" insider the container
   $ root@0529cde0b988:/opt/code# ./pipeline.sh
   or $ root@0529cde0b988:/opt/code# python3 pipeline.py

   # Get 3d model result named as "dense.0.ply"
   After the container was executed successfully with image data files, user should be able to see output in your command window like this:
   '''
   Loading option-0000.ply, 48656 vertices ...
   Save to /images/dense.nvm ... done
   Save /images/dense.0.ply ...done
   ----------------------------------------------------------------
   VisualSFM 3D reconstruction, finished
   Totally 23.000 seconds used
   
   The 3D model file was in ply format, it is located inside your image folder, its name is "dense.0.ply".
   path = "/$path_to_image_folder/dense.0.ply"


## Author
suxing liu(suxingliu@gmail.com)

Reference:
VisualSFM
[Anders Damsgaard](mailto:adamsgaard@ucsd.edu) with contributions by Caleb Adams and Connor P Doherty.
Changchang Wu ( wucc1130@gmail.com )
+ Structure from Motion
[1] Changchang Wu, "Towards Linear-time Incremental Structure From Motion", 3DV 2013
[2] Changchang Wu, "VisualSFM: A Visual Structure from Motion System", http://ccwu.me/vsfm/, 2011
+ Bundle Adjustment
[3] Changchang Wu, Sameer Agarwal, Brian Curless, and Steven M. Seitz, "Multicore Bundle Adjustment", CVPR 2011   
+ Feature Detection
[4] Changchang Wu, "SiftGPU: A GPU implementation of Scale Invaraint Feature Transform (SIFT)", http://cs.unc.edu/~ccwu/siftgpu, 2007

COLMAP
https://colmap.github.io
Author: Johannes L. Schoenberger (jsch-at-demuc-dot-de)
@inproceedings{schoenberger2016sfm,
    author={Sch\"{o}nberger, Johannes Lutz and Frahm, Jan-Michael},
    title={Structure-from-Motion Revisited},
    booktitle={Conference on Computer Vision and Pattern Recognition (CVPR)},
    year={2016},
}

@inproceedings{schoenberger2016mvs,
    author={Sch\"{o}nberger, Johannes Lutz and Zheng, Enliang and Pollefeys, Marc and Frahm, Jan-Michael},
    title={Pixelwise View Selection for Unstructured Multi-View Stereo},
    booktitle={European Conference on Computer Vision (ECCV)},
    year={2016},
}


Docker container was maintained by Wesley Paul Bonelli. it was deployed to Plant IT website by Wesley Paul Bonelli (wbonelli@uga.edu).

Singularity container overlay issues were solved by [Saravanaraj Ayyampalayam] (https://github.com/raj76) (mailto:raj76@uga.edu)

Special thanks to Chris Cotter building the container recipe for testing and debugging.

## Todo
- GPU cuda version container

## License
GNU Public License
