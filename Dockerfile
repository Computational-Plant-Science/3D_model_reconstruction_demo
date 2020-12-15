FROM ubuntu:16.04

LABEL maintainer="Chris Cotter, Suxing Liu, Wes Bonelli"

RUN mkdir -p /opt/code
COPY / /opt/code

RUN apt update && \
    apt install -y \
    wget \
    build-essential \
    python3 \
    unzip \
    glew-utils \
    imagemagick \
    libgtk2.0-dev \
    libglew-dev \
    libdevil-dev \
    libboost-all-dev \
    libatlas-cpp-0.6-dev \
    libatlas-dev \
    libatlas-base-dev \
    liblapack3 \
    libblas3 \
    libblas-dev \
    libcminpack-dev \
    libgfortran3 \
    libmetis-edf-dev \
    libparmetis-dev \
    libjpeg-turbo8 \
    libgsl-dev \
    freeglut3-dev

RUN cd /opt/code && \
    make clean && \
    make all && \
    mkdir /lscratch /db /work /scratch && \
    chmod -R a+rwx /opt/code

ENV PATH=$PATH:/opt/code/vsfm/bin/
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/code/vsfm/bin/

RUN mkdir /opt/code/vsfm/bin/temp && \
    touch /opt/code/vsfm/bin/temp.pgm && \
    touch /opt/code/vsfm/bin/temp/temp.pgm && \
    ls -s /opt/code/vsfm/bin/temp/temp.pgm /opt/code/vsfm/bin/temp.pgm

