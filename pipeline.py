"""
Version: 1.0

Summary: 3D reconstruction pipeline

Author: Suxing Liu, Wesley Paul Bonelli

Author-email: suxingliu@gmail.com, wbonelli@uga.edu

Usage: python3 pipeline.py -i <input directory> -o <output directory> -g <True or False>

Arguments:
("-i", "--input_directory", required=True, help="where to find input image files")
("-o", "--output_directory", required=True, help="where to write output files")
("-s", "--segmentation", required=False, default=False, help="whether to apply root segmentation to images")
("-bd", "--blur_detection", required=False, default=False, help="whether to apply blur detection and omit blurry images")
("-gc", "--gamma_correction", required=False, default=False, help="whether to apply gamma correction to images"
("-g", "--gpu", required=False, default=False, help="whether to use GPUs")
"""
import distutils
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


def reconstruct(
        input_directory,
        output_directory,
        segmentation,
        blur_detection,
        gamma_correction,
        gpu):
    if not os.path.exists(input_directory):
        raise ValueError("Input directory does not exist!")

    if segmentation:
        paths = [join(input_directory, file) for file in listdir(input_directory) if isfile(join(input_directory, file))]
        print("Preprocessing " + str(len(paths)) + " files:")
        pprint.pprint(paths)
        preprocessed_directory = Path('preprocessed')
        preprocessed_directory.mkdir(exist_ok=True)
        path_args = [(path, preprocessed_directory.absolute()) for path in paths]
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            pool.starmap(foreground_substractor, path_args)

    # TODO blur detection and gamma correction

    start = time.time()
    database = join(output_directory, 'database.db')

    # feature extraction
    # last two options prevent memory overconsumption in CPU mode https://colmap.github.io/faq.html#available-functionality-without-gpu-cuda
    subprocess.run("colmap feature_extractor --image_path " + input_directory + " --database_path " + database + ('' if gpu else ' --SiftExtraction.use_gpu=0 --SiftExtraction.num_threads=2 --SiftExtraction.first_octave 0'), shell=True)

    # feature matching
    # might need to use --SiftMatching.max_num_matches as per https://colmap.github.io/faq.html#feature-matching-fails-due-to-illegal-memory-access
    subprocess.run("colmap exhaustive_matcher --database_path " + database + " --SiftMatching.use_gpu=" + str(gpu), shell=True)

    # build sparse model
    sparse = join(output_directory, 'sparse')
    subprocess.run("mkdir " + sparse, shell=True)
    subprocess.run("colmap mapper --database_path " + database + " --image_path " + input_directory + " --output_path " + sparse, shell=True)

    # convert models
    subprocess.run("colmap model_converter --input_path " + join(sparse, '0') + " --output_path " + join(output_directory, 'sparse.nvm') + " --output_type NVM", shell=True)
    subprocess.run("colmap model_converter --input_path " + join(sparse, '0') + " --output_path " + join(output_directory, 'sparse.ply') + " --output_type PLY", shell=True)

    # dense model reconstruction
    subprocess.run("mkdir " + join(output_directory, 'dense'), shell=True)
    if gpu:
        subprocess.run("colmap image_undistorter --image_path " + input_directory + " --input_path " + join(output_directory, 'sparse', '0') + " --output_path " + join(output_directory, 'dense') + " --output_type COLMAP --max_image_size 2000", shell=True)
        subprocess.run("colmap patch_match_stereo --workspace_path " + join(output_directory,'dense') + " --workspace_format COLMAP --PatchMatchStereo.geom_consistency true", shell=True)
        subprocess.run("colmap stereo_fusion --workspace_path " + join(output_directory, 'dense') + " --workspace_format COLMAP --input_type geometric --output_path " + join(output_directory, 'dense.ply'), shell=True)
        subprocess.run("colmap poisson_mesher --input_path " + join(output_directory, 'dense.ply') + " --output_path " + join(output_directory, 'mesh.ply'), shell=True)
    else:
        subprocess.run("colmap image_undistorter --image_path " + input_directory + " --input_path " + join(output_directory, 'sparse', '0') + " --output_path " + join(output_directory, 'dense') + " --output_type PMVS --max_image_size 2000", shell=True)
        subprocess.run("pmvs2 " + join(output_directory, 'dense', 'pmvs') + "/ option-all", shell=True)
        subprocess.run("mv " + join(output_directory, 'dense', 'pmvs', 'models', 'option-all.ply') + " " + join(output_directory, 'dense.ply'), shell=True)


    end = time.time()
    print("Finished in " + str(timedelta(seconds=(end - start))))


# adapted from https://stackoverflow.com/a/43357954/6514033
def str2bool(v):
    return bool(distutils.util.strtobool(v))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input_directory", required=True, help="where to find input images")
    ap.add_argument("-o", "--output_directory", required=False, default=".", help="where to write results")
    ap.add_argument("-s", "--segmentation", type=str2bool, nargs='?', const=True, default=False, help="whether to apply root segmentation to images")
    ap.add_argument("-bd", "--blur_detection", type=str2bool, nargs='?', const=True, default=False, help="whether to apply blur detection and omit blurry images")
    ap.add_argument("-gc", "--gamma_correction", type=str2bool, nargs='?', const=True, default=False, help="whether to apply gamma correction to images")
    ap.add_argument("-g", "--gpu", type=str2bool, nargs='?', const=True, default=False, help="whether to use GPUs")
    args = vars(ap.parse_args())

    reconstruct(
        args["input_directory"],
        args["output_directory"],
        bool(args["segmentation"]),
        bool(args["blur_detection"]),
        bool(args["gamma_correction"]),
        bool(args["gpu"]))
