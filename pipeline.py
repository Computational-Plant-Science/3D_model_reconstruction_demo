"""
Version: 1.0

Summary: 3D reconstruction pipeline

Author: Suxing Liu

Author-email: suxingliu@gmail.com

Usage: python3 pipeline.py -i <input directory> -o <output directory>

Arguments:
("-i", "--input_directory", required=True, help="folder to find input images in")
("-o", "--output_directory", required=True, help="where to write output files to")
("-s", "--segmentation", required=False, default=False, help="whether to apply root segmentation")
("-b", "--blur_detection", required=False, default=False, help="whether to omit blurry images")
("-c", "--correct_gamma", required=False, default=False, help="whether to apply gamma correction"
("-g", "--gpu", required=False, default=False, help="whether to use GPUs")
"""
from distutils import util
import multiprocessing
import subprocess
import argparse
import os
import os.path
import time
from datetime import timedelta
from os import listdir
from os.path import join, isfile
from pathlib import Path

from model_preprocess.bbox_seg import foreground_substractor
from model_preprocess.blur_detector_image import detect_blur
from model_preprocess.gamma_correct import correct_gamma


def reconstruct(
        input_directory,
        output_directory,
        segmentation,
        blur_detection,
        gamma_correction,
        gpu):
    if not os.path.exists(input_directory):
        raise ValueError("Input directory does not exist!")

    # start timing preprocessing
    start = time.time()

    # preprocessing steps
    if segmentation:
        seg_paths = [join(input_directory, file) for file in listdir(input_directory) if isfile(join(input_directory, file))]
        if len(seg_paths) < 2: raise ValueError("Not enough files (" + str(len(seg_paths)) + ")")

        seg_dir = Path('segmented')
        seg_dir.mkdir(exist_ok=True)
        seg_args = [(path, seg_dir.absolute()) for path in seg_paths]
        input_directory = str(seg_dir.absolute())  # update input dir

        print("Segmenting " + str(len(seg_paths)) + " file(s)")
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            pool.starmap(foreground_substractor, seg_args)
    if blur_detection:
        bo_paths = [join(input_directory, file) for file in listdir(input_directory) if isfile(join(input_directory, file))]
        if len(bo_paths) < 2: raise ValueError("Not enough files (" + str(len(bo_paths)) + ")")

        bo_dir = Path('blur_omitted')
        bo_dir.mkdir(exist_ok=True)
        bo_args = [(path, bo_dir.absolute()) for path in bo_paths]
        input_directory = str(bo_dir.absolute())  # update input dir

        print("Applying blur detection to " + str(len(bo_paths)) + " file(s)")
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            pool.starmap(detect_blur, bo_args)
    if gamma_correction:
        gc_paths = [join(input_directory, file) for file in listdir(input_directory) if isfile(join(input_directory, file))]
        if len(gc_paths) < 2: raise ValueError("Not enough files (" + str(len(gc_paths)) + ")")

        gc_dir = Path('gamma_corrected')
        gc_dir.mkdir(exist_ok=True)
        gc_args = [(path, gc_dir.absolute()) for path in gc_paths]
        input_directory = str(gc_dir.absolute())  # update input dir

        print("Applying gamma correction to " + str(len(gc_paths)) + " file(s)")
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            pool.starmap(correct_gamma, gc_args)

    end = time.time()
    print("Preprocessing completed in " + str(timedelta(seconds=(end - start))))

    recon_paths = [join(input_directory, file) for file in listdir(input_directory) if isfile(join(input_directory, file))]
    if len(recon_paths) < 2: raise ValueError("Not enough files for reconstruction (" + str(len(recon_paths)) + ")")
    print("Starting reconstruction from " + str(len(recon_paths)) + " files")
    start = time.time()

    # feature extraction
    database_path = join(output_directory, 'database.db')
    subprocess.run("colmap feature_extractor --image_path " + input_directory + " --database_path " + database_path + \
                   # last 2 options prevent memory overconsumption with CPU https://colmap.github.io/faq.html#available-functionality-without-gpu-cuda
                   ('' if gpu else ' --SiftExtraction.use_gpu=0 --SiftExtraction.num_threads=2 --SiftExtraction.first_octave 0'), shell=True)

    # feature matching
    # TODO might need --SiftMatching.max_num_matches as per https://colmap.github.io/faq.html#feature-matching-fails-due-to-illegal-memory-access
    subprocess.run("colmap exhaustive_matcher --database_path " + database_path + " --SiftMatching.use_gpu=" + str(gpu), shell=True)

    # build sparse model
    outer_sparse_dir = Path(join(output_directory, 'sparse'))
    outer_sparse_dir.mkdir(exist_ok=True)
    inner_sparse_dir_path = join(output_directory, 'sparse', '0')
    sparse_model_path = join(output_directory, 'sparse.ply')
    subprocess.run("colmap mapper --database_path " + database_path + " --image_path " + input_directory + \
                   " --output_path " + str(outer_sparse_dir.absolute()), shell=True)
    subprocess.run("colmap model_converter --input_path " + inner_sparse_dir_path + \
                   " --output_path " + sparse_model_path + " --output_type PLY", shell=True)

    # build dense model
    dense_dir = Path(join(output_directory, 'dense'))
    dense_dir.mkdir(exist_ok=True)
    dense_dir_path = str(dense_dir.absolute())
    if gpu:
        subprocess.run("colmap image_undistorter --image_path " + input_directory + " --input_path " + inner_sparse_dir_path + " --output_path " + \
                       dense_dir_path + " --output_type COLMAP --max_image_size 2000", shell=True)
        subprocess.run("colmap patch_match_stereo --workspace_path " + dense_dir_path + \
                       "--workspace_format COLMAP --PatchMatchStereo.geom_consistency true", shell=True)

        dense_model_path = join(output_directory, 'dense.ply')
        subprocess.run("colmap stereo_fusion --workspace_path " + join(output_directory, 'dense') + \
                       "--workspace_format COLMAP --input_type geometric --output_path " + dense_model_path, shell=True)

        mesh_model_path = join(output_directory, 'mesh.ply')
        subprocess.run("colmap poisson_mesher --input_path " + dense_model_path + " --output_path " + mesh_model_path, shell=True)
    else:
        subprocess.run("colmap image_undistorter --image_path " + input_directory + " --input_path " + join(output_directory, 'sparse', '0') + \
                       " --output_path " + join(output_directory, 'dense') + " --output_type PMVS --max_image_size 2000", shell=True)
        subprocess.run("pmvs2 " + join(output_directory, 'dense', 'pmvs') + "/ option-all", shell=True)
        subprocess.run("mv " + join(output_directory, 'dense', 'pmvs', 'models', 'option-all.ply') + " " + join(output_directory, 'dense.ply'),
                       shell=True)

    end = time.time()
    print("Reconstruction completed in " + str(timedelta(seconds=(end - start))))


# adapted from https://stackoverflow.com/a/43357954/6514033
def str2bool(v):
    return bool(util.strtobool(v))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input_directory", required=True, help="folder to find input images in")
    ap.add_argument("-o", "--output_directory", required=False, default=".", help="folder to write results to")
    ap.add_argument("-s", "--segmentation", type=str2bool, nargs='?', const=True, default=False, help="whether to apply root segmentation")
    ap.add_argument("-b", "--blur_detection", type=str2bool, nargs='?', const=True, default=False, help="whether to omit blurry images")
    ap.add_argument("-c", "--gamma_correction", type=str2bool, nargs='?', const=True, default=False, help="whether to apply gamma correction")
    ap.add_argument("-g", "--gpu", type=str2bool, nargs='?', const=True, default=False, help="whether to use GPUs")
    args = vars(ap.parse_args())

    reconstruct(
        args["input_directory"],
        args["output_directory"],
        bool(args["segmentation"]),
        bool(args["blur_detection"]),
        bool(args["gamma_correction"]),
        bool(args["gpu"]))
