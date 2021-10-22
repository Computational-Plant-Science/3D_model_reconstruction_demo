"""
Version: 1.0

Summary: 3D reconstruction pipeline

Author: Suxing Liu, Wesley Paul Bonelli

Author-email: suxingliu@gmail.com, wbonelli@uga.edu

Usage: python3 pipeline.py -i <input directory> -o <output directory>

Arguments:
("-i", "--input_directory", required=True, help="folder to find input images in")
("-o", "--output_directory", required=True, help="where to write output files to")
("-s", "--segmentation", required=False, default=False, help="whether to apply root segmentation")
("-b", "--blur_detection", required=False, default=False, help="whether to omit blurry images")
("-c", "--correct_gamma", required=False, default=False, help="whether to apply gamma correction"
("-g", "--gpu", type=int, default=0, help="how many GPUs to use (set to 0 for CPUs-only)")
"""
from distutils import util
import multiprocessing
import subprocess
import argparse
import os
import os.path
import time
import csv
from datetime import timedelta
from os import listdir
from os.path import join, isfile
from pathlib import Path

import humanize

from model_preprocess.bbox_seg import foreground_substractor
from model_preprocess.blur_detector_image import detect_blur
from model_preprocess.gamma_correct import correct_gamma


def reconstruct(
        input_directory,
        output_directory,
        segmentation,
        blur_detection,
        gamma_correction,
        gpus):
    if not os.path.exists(input_directory): raise ValueError("Input directory does not exist!")

    # precompute GPU index
    gpu_index = ','.join([str(i) for i in range(0, gpus)])
    if gpus:
        print("Using " + str(gpus) + " GPU" + ("s" if gpus > 1 else ""))
    else:
        print("Not using GPUs")

    # start timing
    start = time.time()
    start_all = time.time()

    # preprocessing steps
    if segmentation:
        seg_paths = [join(input_directory, file) for file in listdir(input_directory) if isfile(join(input_directory, file))]
        if len(seg_paths) < 2: raise ValueError("Not enough files (" + str(len(seg_paths)) + ")")

        seg_dir = Path(join(output_directory, 'segmented'))
        seg_dir.mkdir(exist_ok=True)
        seg_args = [(path, seg_dir.absolute()) for path in seg_paths]
        input_directory = str(seg_dir.absolute())

        print("Segmenting " + str(len(seg_paths)) + " file(s)")
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            pool.starmap(foreground_substractor, seg_args)
    if blur_detection:
        bo_paths = [join(input_directory, file) for file in listdir(input_directory) if isfile(join(input_directory, file))]
        if len(bo_paths) < 2: raise ValueError("Not enough files (" + str(len(bo_paths)) + ")")

        bo_dir = Path(join(output_directory, 'blur_omitted'))
        bo_dir.mkdir(exist_ok=True)
        bo_args = [(path, bo_dir.absolute()) for path in bo_paths]
        input_directory = str(bo_dir.absolute())

        print("Applying blur detection to " + str(len(bo_paths)) + " file(s)")
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            pool.starmap(detect_blur, bo_args)
    if gamma_correction:
        gc_paths = [join(input_directory, file) for file in listdir(input_directory) if isfile(join(input_directory, file))]
        if len(gc_paths) < 2: raise ValueError("Not enough files (" + str(len(gc_paths)) + ")")

        gc_dir = Path(join(output_directory, 'gamma_corrected'))
        gc_dir.mkdir(exist_ok=True)
        gc_args = [(path, gc_dir.absolute()) for path in gc_paths]
        input_directory = str(gc_dir.absolute())

        print("Applying gamma correction to " + str(len(gc_paths)) + " file(s)")
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            pool.starmap(correct_gamma, gc_args)

    end = time.time()
    preprocessing_delta = timedelta(seconds=(end - start))
    print("Preprocessing completed in " + humanize.naturaldelta(preprocessing_delta))
    start = time.time()

    # make sure we have enough files to run the reconstruction (TODO: is 2 a reasonable minimum?)
    image_paths = [join(input_directory, file) for file in listdir(input_directory) if isfile(join(input_directory, file))]
    if len(image_paths) < 2: raise ValueError("Not enough images to begin reconstruction (" + str(len(image_paths)) + ")")
    print("Starting feature extraction from " + str(len(image_paths)) + " images")

    # feature extraction
    database_path = join(output_directory, 'database.db')
    subprocess.run("colmap feature_extractor --image_path " + input_directory + " --database_path " + database_path + \
                   ((' --SiftExtraction.gpu_index=' + gpu_index) if gpus else ' --SiftExtraction.use_gpu=0 '
                                                                                  # last 2 options prevent memory overconsumption with CPU
                                                                                  # https://colmap.github.io/faq.html#available-functionality-without-gpu-cuda
                                                                                  '--SiftExtraction.num_threads=2 '
                                                                                  '--SiftExtraction.first_octave 0'), shell=True)

    end = time.time()
    feature_extraction_delta = timedelta(seconds=(end - start))
    print("Feature extraction completed in " + humanize.naturaldelta(feature_extraction_delta) + ", starting feature matching")
    start = time.time()

    # feature matching
    # TODO might need --SiftMatching.max_num_matches as per https://colmap.github.io/faq.html#feature-matching-fails-due-to-illegal-memory-access
    subprocess.run("colmap exhaustive_matcher --database_path " + database_path + \
                   ((' --SiftMatching.gpu_index=' + gpu_index) if gpus else ' --SiftExtraction.use_gpu=0'), shell=True)

    end = time.time()
    feature_matching_delta = timedelta(seconds=(end - start))
    print("Feature matching completed in " + humanize.naturaldelta(feature_matching_delta) + ", building sparse model")
    start = time.time()

    # build sparse model
    outer_sparse_dir = Path(join(output_directory, 'sparse'))
    outer_sparse_dir.mkdir(exist_ok=True)
    inner_sparse_dir_path = join(output_directory, 'sparse', '0')
    sparse_model_path = join(output_directory, 'sparse.ply')
    subprocess.run("colmap mapper --database_path " + database_path + " --image_path " + input_directory + \
                   " --output_path " + join(outer_sparse_dir.parent.stem, outer_sparse_dir.stem), shell=True)
    subprocess.run("colmap model_converter --input_path " + inner_sparse_dir_path + \
                   " --output_path " + sparse_model_path + " --output_type PLY", shell=True)

    end = time.time()
    sparse_model_delta = timedelta(seconds=(end - start))
    print("Sparse model completed in " + humanize.naturaldelta(sparse_model_delta) + ", building dense model")
    start = time.time()

    # build dense model
    dense_dir = Path(join(output_directory, 'dense'))
    dense_dir.mkdir(exist_ok=True)
    dense_dir_path = str(dense_dir.absolute())
    if gpus:
        # image undistortion
        subprocess.run("colmap image_undistorter --image_path " + input_directory + " --input_path " + inner_sparse_dir_path + " --output_path " + \
                       dense_dir_path + " --output_type COLMAP --max_image_size 2000", shell=True)

        # patch match
        # TODO make geom_consistency/filter optional, maybe other optimizations here https://colmap.github.io/faq.html#speedup-dense-reconstruction
        subprocess.run("colmap patch_match_stereo --workspace_path " + dense_dir_path + \
                       " --workspace_format COLMAP --PatchMatchStereo.geom_consistency false --PatchMatchStereo.filter true" + \
                       ((' --PatchMatchStereo.gpu_index=' + gpu_index) if gpus else ''), shell=True)

        # stereo fusion
        dense_model_path = join(output_directory, 'dense.ply')
        subprocess.run("colmap stereo_fusion --workspace_path " + join(output_directory, 'dense') + \
                       " --workspace_format COLMAP --input_type geometric --output_path " + dense_model_path, shell=True)

        # generate mesh
        mesh_model_path = join(output_directory, 'mesh.ply')
        subprocess.run("colmap poisson_mesher --input_path " + dense_model_path + " --output_path " + mesh_model_path, shell=True)
    else:
        # image undistortion
        subprocess.run("colmap image_undistorter --image_path " + input_directory + " --input_path " + join(output_directory, 'sparse', '0') + \
                       " --output_path " + join(output_directory, 'dense') + " --output_type PMVS --max_image_size 2000", shell=True)

        # PMVS2 for CPU dense reconstruction
        subprocess.run("pmvs2 " + join(output_directory, 'dense', 'pmvs') + "/ option-all", shell=True)
        subprocess.run("mv " + join(output_directory, 'dense', 'pmvs', 'models', 'option-all.ply') + \
                       " " + join(output_directory, 'dense.ply'),  # move the model to the output dir
                       shell=True)

    end = time.time()
    dense_model_delta = timedelta(seconds=(end - start))
    print("Dense model completed in " + humanize.naturaldelta(dense_model_delta))

    total_delta = timedelta(seconds=(end - start_all))
    print("Reconstruction completed in " + humanize.naturaldelta(total_delta))

    # write time cost data to CSV
    with open(join(output_directory, 'times.csv'), 'w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['preprocessing', 'feature_extraction', 'feature_matching', 'sparse_model', 'dense_model'])
        writer.writerow([
            preprocessing_delta.total_seconds(),
            feature_matching_delta.total_seconds(),
            feature_matching_delta.total_seconds(),
            sparse_model_delta.total_seconds(),
            dense_model_delta.total_seconds()])


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
    ap.add_argument("-g", "--gpus", type=int, default=0, help="how many GPUs to use (set to 0 for CPUs-only)")
    args = vars(ap.parse_args())

    reconstruct(
        args["input_directory"],
        args["output_directory"],
        bool(args["segmentation"]),
        bool(args["blur_detection"]),
        bool(args["gamma_correction"]),
        int(args["gpus"]))
