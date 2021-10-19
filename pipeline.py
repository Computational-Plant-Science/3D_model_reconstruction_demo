"""
Version: 1.0

Summary: 3D reconstruction pipeline (colmap+VSFM for CPU, colmap-only for GPU)

Author: Suxing Liu

Author-email: suxingliu@gmail.com

Usage: python3 pipeline.py <input directory> -o <output directory> -p <True or False> -g <True or False>

Arguments:
("-i", "--input_diirectory", required = True, help = "where to find input image files")
("-o", "--output_directory", required = True, help = "where to write output files")
("-p", "--preprocess", required = False, help = "whether to preprocess images, defaults to False")
("-g", "--gpu", required = False, default = False, help = "whether to use GPUs")
"""
import multiprocessing
import subprocess

import argparse
import os
import os.path
import time
from datetime import timedelta
from os import listdir
from os.path import join, isfile

import pprint
from pathlib import Path

from model_preprocess.bbox_seg import foreground_substractor


def reconstruct(source: str, output_directory: str, preprocess: bool, gpu: bool):
    if not os.path.exists(source):
        raise ValueError("Path does not exist!")

    if preprocess:
        paths = [join(source, file) for file in listdir(source) if isfile(join(source, file))]
        print("Preprocessing " + str(len(paths)) + " files:")
        pprint.pprint(paths)
        preprocessed_directory = Path('preprocessed')
        preprocessed_directory.mkdir(exist_ok=True)
        path_args = [(path, preprocessed_directory.absolute()) for path in paths]
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            pool.starmap(foreground_substractor, path_args)

    start = time.time()
    database = join(output_directory, 'database.db')

    # feature extraction
    # last two options prevent memory overconsumption in CPU mode https://colmap.github.io/faq.html#available-functionality-without-gpu-cuda
    subprocess.run("colmap feature_extractor --image_path " + source + " --database_path " + database + ('' if gpu else ' --SiftExtraction.use_gpu=0 --SiftExtraction.num_threads=2 --SiftExtraction.first_octave 0'), shell=True)

    # feature matching
    # might need to use --SiftMatching.max_num_matches as per https://colmap.github.io/faq.html#feature-matching-fails-due-to-illegal-memory-access
    subprocess.run("colmap exhaustive_matcher --database_path " + database + " --SiftMatching.use_gpu=" + str(gpu), shell=True)

    # build sparse model
    sparse = join(output_directory, 'sparse')
    subprocess.run("mkdir " + sparse, shell=True)
    subprocess.run("colmap mapper --database_path " + database + " --image_path " + source + " --output_path " + sparse, shell=True)

    # convert models
    subprocess.run("colmap model_converter --input_path " + join(sparse, '0') + " --output_path " + join(output_directory, 'sparse.nvm') + " --output_type NVM", shell=True)
    subprocess.run("colmap model_converter --input_path " + join(sparse, '0') + " --output_path " + join(output_directory, 'sparse.ply') + " --output_type PLY", shell=True)

    # dense model reconstruction (colmap on GPU, VSFM on CPU)
    if gpu:
        subprocess.run("mkdir " + join(output_directory, 'dense'), shell=True)
        subprocess.run("colmap image_undistorter --image_path " + source + " --input_path " + join(output_directory, 'sparse', '0') + " --output_path " + join(output_directory, 'dense') + " --output_type COLMAP --max_image_size 2000", shell=True)
        subprocess.run("colmap patch_match_stereo --workspace_path " + join(output_directory,'dense') + " --workspace_format COLMAP --PatchMatchStereo.geom_consistency true", shell=True)
        subprocess.run("colmap stereo_fusion --workspace_path " + join(output_directory, 'dense') + " --workspace_format COLMAP --input_type geometric --output_path " + join(output_directory, 'dense.ply'), shell=True)
        subprocess.run("colmap poisson_mesher --input_path " + join(output_directory, 'dense.ply') + " --output_path " + join(output_directory, 'mesh.ply'), shell=True)
    else:
        subprocess.run("/opt/code/vsfm/bin/VisualSFM sfm+loadnvm+pmvs " + join(output_directory, 'model.nvm') + " " + join(output_directory, 'dense.nvm'), shell=True)

    end = time.time()
    print("Finished in " + str(timedelta(seconds=(end - start))))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input_directory", required=True, help="where to find input images")
    ap.add_argument("-o", "--output_directory", required=False, default=".", help="where to write results")
    ap.add_argument("-p", "--preprocess", required=False, default=False, help="whether to preprocess images")
    ap.add_argument("-g", "--gpu", required=False, default=False, help="whether to use GPUs")
    args = vars(ap.parse_args())

    source = args["input_directory"]
    target = args["output_directory"]
    preprocess = args["preprocess"]
    gpu = args["gpu"]

    reconstruct(source, target, preprocess, gpu)
