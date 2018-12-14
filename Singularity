BootStrap: docker
From: ubuntu:16.04 

%help
  Help will go here

%labels
  Maintainer Chris Cotter
  Version v0.01

%post
  apt-get update
  apt -y install \
	git \
    libgtk2.0-dev \
    libglew-dev \
    libdevil-dev \
    libboost-all-dev \
    libatlas-cpp-0.6-dev \
    libatlas-dev \
    imagemagick \
    libatlas3-base \
    libcminpack-dev \
    libgfortran3 \
    libmetis-edf-dev \
    libparmetis-dev \
    freeglut3-dev \
    libgsl-dev \
    
  cd /opt
  git clone https://github.com/lsx1980/vsfm-master.git
  cd /opt/vsfm-master

%environment
  PATH=$PATH:/opt/vsfm-master/vsfm/bin/
  LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/vsfm-master/vsfm/bin/

%runscript
  /opt/vsfm-master/vsfm/bin/VisualSFM "$@"
