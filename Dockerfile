FROM ubuntu:20.04

LABEL maintainer="Suxing Liu, Wes Bonelli"

#setup working directory
RUN mkdir -p /opt/code/
COPY ./* /opt/code/

WORKDIR /opt/code

# Install dependencies for VSFM
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    wget \
    build-essential \
    cmake \
    unzip \
    tzdata \
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



# Get dependencies for colmap
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    graphviz \
    git \
    coinor-libclp-dev \
    libceres-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libxi-dev \
    libxinerama-dev \
    libxcursor-dev \
    libxxf86vm-dev \
    libboost-program-options-dev \
    libboost-iostreams-dev \
    libboost-filesystem-dev \
    libboost-serialization-dev \
    libboost-graph-dev \
    libboost-regex-dev \
    libboost-system-dev \
    libboost-test-dev \
    libeigen3-dev \
    libsuitesparse-dev \
    libfreeimage-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libglew-dev \
    qtbase5-dev \
    libcgal-dev \
    libcgal-qt5-dev \
    libqt5opengl5-dev \
    python3-setuptools \
    python3.8 \
    python3.8-distutils


#GLFW3 (Optional)
RUN apt-get -y install freeglut3-dev libglew-dev libglfw3-dev

# Build and install ceres solver
RUN apt-get -y install \
    libatlas-base-dev \
    libsuitesparse-dev
RUN git clone https://github.com/ceres-solver/ceres-solver.git --branch 1.14.0
RUN cd ceres-solver && \
	mkdir build && \
	cd build && \
	cmake .. -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF && \
	make -j4 && \
	make install

# Build latest COLMAP
RUN git clone https://github.com/colmap/colmap.git --branch dev
RUN mkdir comap_build && cd comap_build
RUN cmake . /opt/code/colmap -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="/opt/code"
RUN make -j4 && make install
RUN cd .. ; rm -rf comap_build

# Add binaries to path
ENV PATH $PATH:/opt/code/bin

# Install VisualSFM
ADD http://ccwu.me/vsfm/download/VisualSFM_linux_64bit.zip /opt/code/VisualSFM_linux_64bit.zip
RUN unzip VisualSFM_linux_64bit.zip
RUN cd vsfm; sed -i 's/LIB_LIST +=/LIB_LIST += -no-pie /' /opt/code/vsfm/makefile; make

# Install SiftGPU 
ADD https://github.com/pitzer/SiftGPU/archive/master.zip /opt/code/master.zip
RUN unzip master.zip; mv SiftGPU-master SiftGPU
ADD patches/siftgpu.patch /opt/code/SiftGPU/siftgpu.patch
RUN cd SiftGPU; patch -p0 < siftgpu.patch; make
RUN cp SiftGPU/bin/libsiftgpu.so /opt/code/vsfm/bin

# Install PBA
ADD http://grail.cs.washington.edu/projects/mcba/pba_v1.0.5.zip /opt/code/pba.zip
RUN unzip pba.zip
RUN cd pba; dos2unix makefile_no_gpu
RUN cd pba; make -f makefile_no_gpu; cp -v bin/libpba_no_gpu.so /opt/code/vsfm/bin/libpba.so

#Install CMVS-PMVS
ADD https://github.com/pmoulon/CMVS-PMVS/archive/master.zip /opt/code/master.zip
RUN unzip master.zip; mv CMVS-PMVS-master CMVS-PMVS
RUN mkdir -p CMVS-PMVS/program/build; cd CMVS-PMVS/program/build; cmake ..; make install 
RUN cp CMVS-PMVS/program/build/main/cmvs /opt/code/vsfm/bin/
RUN cp CMVS-PMVS/program/build/main/pmvs2 /opt/code/vsfm/bin/
RUN cp CMVS-PMVS/program/build/main/genOption /opt/code/vsfm/bin/

# Install Graclus
ADD http://www.cs.utexas.edu/users/dml/Software/graclus1.2.tar.gz /opt/code/graclus1.2.tar.gz
RUN tar xzf graclus1.2.tar.gz
ADD patches/graclus.patch /opt/code/graclus1.2/graclus.patch
RUN cd graclus1.2; patch -p0 < graclus.patch; make

# Install vlfeat
ADD http://www.vlfeat.org/download/vlfeat-0.9.19-bin.tar.gz /opt/code/vlfeat-0.9.19-bin.tar.gz
RUN tar xzf vlfeat-0.9.19-bin.tar.gz
RUN cp -v vlfeat-0.9.19/bin/glnxa64/* /opt/code/vsfm/bin/

# aAdd configuration file
ADD config/nv.ini /opt/code/vsfm/bin/nv.ini

ENV PATH $PATH:/opt/code/vsfm/bin
ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:/opt/code/vsfm/bin

RUN mkdir /lscratch /db /work /scratch && \
    chmod -R a+rwx /opt/code

RUN mkdir -p /opt/code/vsfm/bin/log && \
    mkdir -p /opt/code/vsfm/bin/temp/log && \
    touch /opt/code/vsfm/bin/temp/temp.pgm && \
    touch /opt/code/vsfm/bin/temp/temp.sift.sift && \
    ln -s /opt/code/vsfm/bin/temp/temp.pgm /opt/code/vsfm/bin/temp.pgm && \
    ln -s /opt/code/vsfm/bin/temp/temp.sift.sift /opt/code/vsfm/bin/temp.sift.sift && \
    ln -s /opt/code/vsfm/bin/temp/log /opt/code/vsfm/bin/log

RUN python3.8 -m easy_install pip && \
    python3.8 -m pip install --upgrade pip && \
    python3.8 -m pip install -r /opt/code/requirements.txt
