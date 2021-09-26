FROM nvidia/cuda:11.4.2-base-ubuntu20.04

LABEL maintainer="Suxing Liu, Wes Bonelli"

#setup working directory
COPY . /opt/code

WORKDIR /opt/code

RUN apt-get -ym update && \
	DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git \
    wget \
    cmake \
    tzdata \
    build-essential \
    mlocate \
    python3-pip \
    python3 \
    python3-setuptools \
    libboost-program-options-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-regex-dev \
    libboost-system-dev \
    libboost-test-dev \
    libeigen3-dev \
    libsuitesparse-dev \
    libfreeimage-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libglfw3-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    freeglut3-dev \
    libglew-dev \
    libdevil-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    libcgal-dev

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    unzip \
    nano \
    glew-utils \
    imagemagick \
    libgtk2.0-dev \
    libglew-dev \
    libdevil-dev \
    libboost-all-dev \
    libatlas-cpp-0.6-dev \
    libatlas-base-dev \
    libatlas3-base \
    liblapack3 \
    libblas3 \
    libblas-dev \
    libcminpack-dev \
    libgfortran5 \
    libmetis-edf-dev \
    libparmetis-dev \
    libjpeg-turbo8 \
    libgsl-dev \
    freeglut3-dev \
    dos2unix

RUN apt-get -ym install libatlas-base-dev libsuitesparse-dev

RUN git clone https://ceres-solver.googlesource.com/ceres-solver && \
    git clone https://github.com/colmap/colmap.git && \
    git clone https://github.com/pitzer/SiftGPU.git

# Install ceres-solver
RUN cd ceres-solver && \
	git checkout $(git describe --tags) && \
	mkdir build && \
	cd build && \
	cmake .. -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF && \
	make && \
	make install

# Install colmap
RUN cd colmap && \
	git checkout master && \
	mkdir build && \
	cd build && \
	cmake ../ && \
	make && \
	make install

# Install VisualSFM
RUN wget http://ccwu.me/vsfm/download/VisualSFM_linux_64bit.zip && \
	unzip VisualSFM_linux_64bit.zip && \
	rm VisualSFM_linux_64bit.zip && \
	cd vsfm && \
	sed -i 's/LIB_LIST +=/LIB_LIST += -no-pie /' /opt/code/vsfm/makefile && \
	make

# Install SiftGPU
RUN cd SiftGPU && \
    git checkout master && \
	make && \
	cp /opt/code/SiftGPU/bin/libsiftgpu.so /opt/code/vsfm/bin

# Install PBA
RUN wget http://grail.cs.washington.edu/projects/mcba/pba_v1.0.5.zip && \
	unzip pba_v1.0.5.zip && \
	rm pba_v1.0.5.zip && \
	cd /opt/code/pba && \
	dos2unix makefile_no_gpu && \
	make -f makefile_no_gpu && \
	cp -v /opt/code/pba/bin/libpba_no_gpu.so /opt/code/vsfm/bin/libpba.so

#Install CMVS-PMVS
RUN wget https://github.com/pmoulon/CMVS-PMVS/archive/master.zip && \
	unzip master.zip && \
	rm master.zip && \
	mv CMVS-PMVS-master CMVS-PMVS && \
	mkdir -p /opt/code/CMVS-PMVS/program/build && \
	cd /opt/code/CMVS-PMVS/program/build && \
	cmake .. && \
	make install && \
	cp /opt/code/CMVS-PMVS/program/build/main/cmvs /opt/code/vsfm/bin/ && \
	cp /opt/code/CMVS-PMVS/program/build/main/pmvs2 /opt/code/vsfm/bin/ && \
	cp /opt/code/CMVS-PMVS/program/build/main/genOption /opt/code/vsfm/bin/

# Install Graclus
RUN wget http://www.cs.utexas.edu/users/dml/Software/graclus1.2.tar.gz && \
	tar xzf graclus1.2.tar.gz && \
	rm graclus1.2.tar.gz && \
	#cp patches/graclus.patch /opt/code/graclus1.2/graclus.patch && \
	sed -i 's/COPTIONS = -DNUMBITS=32/COPTIONS = -DNUMBITS=64/' /opt/code/graclus1.2/Makefile.in && \
	cd /opt/code/graclus1.2 && \
	make

# Install vlfeat
RUN wget http://www.vlfeat.org/download/vlfeat-0.9.19-bin.tar.gz && \
	tar xzf vlfeat-0.9.19-bin.tar.gz && \
	rm vlfeat-0.9.19-bin.tar.gz && \
	cp -v /opt/code/vlfeat-0.9.19/bin/glnxa64/* /opt/code/vsfm/bin/

# Add configuration file
RUN cp /opt/code/config/nv.ini /opt/code/vsfm/bin/nv.ini

RUN mkdir /lscratch /db /work /scratch && \
    chmod -R a+rwx /opt/code

# Symbolic link vsfm log and temp files
RUN mkdir -p /opt/code/vsfm/bin/log && \
    mkdir -p /opt/code/vsfm/bin/temp/log && \
    touch /opt/code/vsfm/bin/temp/temp.pgm && \
    touch /opt/code/vsfm/bin/temp/temp.sift.sift && \
    ln -s /opt/code/vsfm/bin/temp/temp.pgm /opt/code/vsfm/bin/temp.pgm && \
    ln -s /opt/code/vsfm/bin/temp/temp.sift.sift /opt/code/vsfm/bin/temp.sift.sift && \
    ln -s /opt/code/vsfm/bin/temp/log /opt/code/vsfm/bin/log

# PyQt bug fix
RUN strip --remove-section=.note.ABI-tag /usr/lib/x86_64-linux-gnu/libQt5Core.so

RUN pip3 install --upgrade pip && \
    pip3 install -r /opt/code/requirements.txt

# Set environment variables
ENV PATH=$PATH:/opt/code/vsfm/bin/
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/code/vsfm/bin/

