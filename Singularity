BootStrap: docker
From: ubuntu:16.04

%help
  Help will go here

  Special thanks goes to https://gist.github.com/lvisintini/e07abae48f099b913f9cf1c1f0fe43ba

%labels
  Maintainer Chris Cotter
  Version v0.01

%setup
  mkdir ${SINGULARITY_ROOTFS}/opt/code/

%files
  ./* /opt/code

%post
  #######################################################################################
  # Install dependencies
  apt update
  apt install -y \
      wget \
      build-essential \
      unzip \
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
      glew-utils \
      libblas-dev \
      liblapack-dev

  cd /opt/code
  make clean
  make all

  chmod -R a+rwx /opt/code

%environment
  PATH=$PATH:/opt/code/vsfm/bin/
  export PATH
  LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/code/vsfm/bin/
  export LD_LIBRARY_PATH

%runscript
  /opt/code/vsfm/bin/VisualSFM "$@"
