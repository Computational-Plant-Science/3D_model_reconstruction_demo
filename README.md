# DIRT3D Reconstruction

Reconstruct a 3D point cloud root model from images.
 
For example, a real root and a reconstruction, side by side:

![Optional Text](../master/media/ProjectDemo.gif)
    
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
python3 /opt/code/pipeline.py -i <input directory> -o <output directory> -g <whether to use GPUs>
```

This will produce `sparse.ply` and `dense.ply` files in the output directory.

### Preprocessing

There are several optional preprocessing steps, all of which accept values `True` or `False` (and default to `False`): 

- `-s`/`--segmentation`: crops to the largest feature and throws out blurry images
- `-bd`/`--blur_detection`: detects and omits blurry images
- `-gc`/`--gamma_correction`: increases brightness of dark images

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
