# SFM for 3D root model reconstructure

### Running With Singularity
The singularity container is available on [Singularity Hub](https://www.singularity-hub.org)
and can be run using
```bash
singularity run shub://cottersci/vsfm-master [VisualSFM paramaters]
```

where [VisualSFM paramaters] are the input parameters for VisualSFM. Using the local examples:

```bash
singularity run shub://cottersci/vsfm-master sfm+pairs /$root/Root_image_data/3600_10_whole/PairList_90_2.txt
```

```bash
singularity run shub://cottersci/vsfm-master sfm+pmvs /$root/Tree
```

## Compiling

### Required Dependencies
GTK toolkit development files, freeglut development files, libdevil development
files.

On Ubuntu:

```bash
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
```

### Building

#### Locally
The included Makefile will download and compile the necessary components not included in "Required Dependencies".

```bash
make all
```

#### Singulairty
The singularity container can be built using

```bash
singularity build vsfm.img Singulairty
```

Then run using

```bash
singularity run vsfm.img
```

## Running Locally
```bash
./vsfm-master/vsfm/bin/VisualSFM sfm+pairs /home/suxingliu/Root_image_data/3600_10_whole/PairList_90_2.txt
```

```bash
./vsfm-master/vsfm/bin/VisualSFM sfm+pmvs /home/suxingliu/Tree
```

## Author
suxing liu(suxingliu@gmail.com)
reference:
[Anders Damsgaard](mailto:adamsgaard@ucsd.edu) with contributions by Caleb Adams
and Connor P Doherty.
Changchang Wu ( wucc1130@gmail.com )

Singularity container maintained by [Chris Cotter](http://github.com/cottersci).

## Todo
- VisualSFM is built without CUDA acceleration. Add optional GPU build.
- Add support for CMVS/PMVS2

## License
GNU Public License
