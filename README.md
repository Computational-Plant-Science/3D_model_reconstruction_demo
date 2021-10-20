# DIRT3D Reconstruction

Reconstruct a 3D point cloud root model from images.
 
For example, a real root and a reconstruction, side by side:

![Optional Text](../master/media/ProjectDemo.gif)
    
# Usage

The easiest way to use this software is with Docker or Singularity. There are two versions of the image definition, one for CPUs and one for GPUs. **Note that reconstruction will fail if the GPU image is used on a host without GPU hardware.**

- `computationalplantscience/dirt3d-reconstruction-cpu`: uses colmap for sparse model reconstruction, then VSFM for dense
- `computationalplantscience/dirt3d-reconstruction-gpu`: uses colmap for both sparse and dense models

## Reconstructing a 3D point cloud with GPUs

### Docker

Mount the current working directory and open an interactive shell:

```shell
docker run -it --gpus all -v $(pwd):/opt/dev -w /opt/dev computationalplantscience/dirt3d-reconstruction-gpu bash
```

Then reconstruct a model from a directory of images:

```shell
python3 /opt/code/pipeline.py -i <input directory> -o <output directory> -g True
```

To enable initial pre-processing (crops to the largest feature and throws out blurry images), use the `-p True` flag.

This will produce `sparse.ply`, `dense.ply`, and `mesh.ply` files in the output directory.

### Singularity

Open a shell in your current working directory:

```shell
singularity shell --nv docker://computationalplantscience/dirt3d-reconstruction-gpu
```

Then use the same command to reconstruct a model from a directory of images (see above).

## Visualizing a 3D point cloud

Currently this software does not support model visualization. PLY files can be visualized with e.g. [Meshlab](https://www.meshlab.net/) or [cloudcompare](https://www.danielgm.net/cc/).

# Author
Suxing Liu (suxingliu@gmail.com)

## Dependencies

This software is built on top of COLMAP and VSFM.

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

## Other contributions

Docker container was maintained and deployed to [PlantIT](https://portnoy.cyverse.org) by Wes Bonelli (wbonelli@uga.edu).

Singularity container overlay issues were solved by [Saravanaraj Ayyampalayam] (https://github.com/raj76) (mailto:raj76@uga.edu)

Special thanks to Chris Cotter building the Singularity container recipe for testing and debugging.

# License
GNU Public License
