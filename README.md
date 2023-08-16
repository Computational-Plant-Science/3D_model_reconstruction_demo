# DIRT/3D: 3D root phenotyping system for field-grown maize roots

Pipeline: Build 3D root models from images captured by 3D root scanner, and compute 3D root trait by analyzing 3D root models and computing 3D root model structures.

This repo was to Reconstruct a 3D point cloud root model from images.
 
For example, a real root and a reconstruction, side by side:

![3D root scanner prototype](../master/media/3D_scanner.gif)

![3D root model reconstruction](../master/media/3D_model.gif)
    
# Installation

The easiest way to use this software is with Docker or Singularity. A public Docker image definition is available: `computationalplantscience/dirt3d-reconstruction`

## Docker

Pull an image or a repository from a registry
```shell
docker pull computationalplantscience/dirt3d-reconstruction
```
Mount the current working directory and open an interactive shell:

```shell
docker run -it -v $(pwd):/opt/dev -w /opt/dev computationalplantscience/dirt3d-reconstruction bash
```

To allow `colmap` to use CUDA-enabled GPUs, use `--gpus all`.

## Singularity

Open a shell in your current working directory:

```shell
singularity shell docker://computationalplantscience/dirt3d-reconstruction
```

To allow `colmap` to use CUDA-enabled GPUs, use the `--nv` flag.

# Usage

## Reconstructing a 3D point cloud

To reconstruct a point cloud from an image set, use `pipeline.py` as such:

```shell
python3 /opt/code/pipeline.py -i <input directory> -o <output directory> -g <how many GPUs to use>
```

Omit the `-g <# of GPUs>` argument or set it to 0 to perform the reconstruction with CPUs only. Note that `-g <# GPUs>` is short for `--gpus <# GPUs>`.

A successful reconstruction will produce several files in the output directory:

- `sparse.ply`: sparse point cloud model
- `dense.ply`: dense point cloud model
- `mesh.ply`: dense mesh model
- `times.csv`: time costs per step

### Preprocessing

There are several optional preprocessing steps, all of which accept values `True` or `False` (and default to `False`): 

- `--segmentation`: crops to the largest feature
- `--blur_detection`: detects and omits blurry images
- `--gamma_correction`: increases brightness of dark images

### PMVS2 vs. Colmap for dense reconstruction

By default, PMVS2 is used for dense reconstruction on both CPU and GPU. Colmap can optionally be used with GPUs. It tends to produce significantly denser models but may run up to an order of magnitude more slowly.

To enable dense reconstruction with Colmap, use `-d COLMAP` (short for `--dense_strategy COLMAP`).

#### Colmap configuration

There are several configurable values for colmap's patch matching step during dense reconstruction. Optimal values will vary by host machine.

- `--cache_size`: cache size (in GB) to use during patch matching, defaults to `32`
- `--window_step`: patch window step size, defaults to `1`
- `--window_radius`: patch window radius, defaults to `5`
- `--num_iterations`: number of patch match iterations, defaults to `5`
- `--num_samples`: number of sampled views, defaults to `15`
- `--geom_consistency`: whether to perform geometric dense reconstruction, defaults to `False`

## Visualizing a 3D point cloud

Currently this software does not support model visualization. PLY files can be visualized with e.g. [Meshlab](https://www.meshlab.net/) or [cloudcompare](https://www.danielgm.net/cc/).

# Dependencies

This software is built on top of COLMAP, VSFM, & PMVS2.

### VisualSFM
[Anders Damsgaard](mailto:adamsgaard@ucsd.edu) with contributions by Caleb Adams and Connor P Doherty.
Changchang Wu ( wucc1130@gmail.com )
+ Structure from Motion
[1] Changchang Wu, "Towards Linear-time Incremental Structure From Motion", 3DV 2013
[2] Changchang Wu, "VisualSFM: A Visual Structure from Motion System", http://ccwu.me/vsfm/, 2011
+ Bundle Adjustment
[3] Changchang Wu, Sameer Agarwal, Brian Curless, and Steven M. Seitz, "Multicore Bundle Adjustment", CVPR 2011   
+ Feature Detection
[4] Changchang Wu, "SiftGPU: A GPU implementation of Scale Invaraint Feature Transform (SIFT)", http://cs.unc.edu/~ccwu/siftgpu, 2007

### COLMAP
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

# Author
Suxing Liu (suxingliu@gmail.com), Wesley Paul Bonelli(wbonelli@uga.edu)

## Other contributions

Docker container was maintained and deployed to [PlantIT](https://portnoy.cyverse.org) by Wes Bonelli (wbonelli@uga.edu).

Singularity container overlay issues were solved by [Saravanaraj Ayyampalayam] (https://github.com/raj76) (mailto:raj76@uga.edu)

Special thanks to Chris Cotter building the Singularity container recipe for testing and debugging.

# License
GNU Public License
