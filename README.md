# SFM for 3D root model reconstructure

### Running With Singularity
The singularity container is available on [Singularity Hub](https://www.singularity-hub.org)
and can be run using
```bash
singularity run shub://cottersci/vsfm-master [VisualSFM paramaters]
```

where [VisualSFM paramaters] are the input parameters for VisualSFM. Using the local examples:

```bash
singularity run shub://cottersci/vsfm-master sfm+pairs /$root/$path_to_your_pairlist_file/
```

```bash
singularity run shub://cottersci/vsfm-master sfm+pmvs /$root/$path_to_your_image_file_folder/
```

## Compiling

### Required Dependencies
GTK toolkit development files, freeglut development files, libdevil development
files.

On Ubuntu:

```bash
apt update
  apt install -y \
      wget \
      build-essential \
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
singularity build --writable vsfm.img Singularity
```

Then run using

```bash
singularity exec --writable vsfm.img /opt/code/vsfm/bin/VisualSFM  sfm+pmvs /$root/$path_to_your_image_file_folder/
```

## Running Locally
```bash
./opt/code/vsfm/bin/VisualSFM sfm+pairs /$root/$path_to_your_pairlist_file/
```

```bash
./opt/code/vsfm/bin/VisualSFM sfm+pmvs /$root/$path_to_your_image_file_folder/
```

## Author
suxing liu(suxingliu@gmail.com)
reference:
[Anders Damsgaard](mailto:adamsgaard@ucsd.edu) with contributions by Caleb Adams
and Connor P Doherty.
Changchang Wu ( wucc1130@gmail.com )

Singularity container maintained by [Chris Cotter](http://github.com/cottersci).
Singularity container overlay issue solved by [Saravanaraj Ayyampalayam] (https://github.com/raj76) (mailto:raj76@uga.edu)


## Todo
- VisualSFM is built without CUDA acceleration. Add optional GPU build.
- Add support for CMVS/PMVS2
- support GPU based SIFT feature matching

## License
GNU Public License
