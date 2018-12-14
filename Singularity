BootStrap: docker
From: debian:stretch

%help
  Help will go here

%labels
  Maintainer Chris Cotter
  Version v0.01

%post
  apt-get update
  #apt-get -y install build-essential git
  apt-get install -y git

  cd /opt
  git clone https://github.com/lsx1980/vsfm-master.git
  cd /opt/vsfm-master
  apt-get install -y libgtk2.0-dev freeglut3-dev libdevil-dev libglew-dev unzip liblapack-dev

%runscript
  /opt/vsfm-master/vsfm/bin/VisualSFM "$@"
