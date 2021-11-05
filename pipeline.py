"""
Version: 1.0

Summary: 3D reconstruction pipeline

Author: Suxing Liu, Wesley Bonelli

Author-email: suxingliu@gmail.com, wbonelli@uga.edu

Usage: python3 pipeline.py -i <input directory> -o <output directory>

Arguments:
("-i", "--input_directory", required=True, help="folder to find input images in")
("-o", "--output_directory", required=False, default=".", help="folder to write results to")
("--bounding_box", type=str2bool, nargs='?', const=True, default=False, help="whether to detect the root boundary and crop to a bounding box")
("--mask_segmentation", type=str2bool, nargs='?', const=True, default=False, help="whether to segment and mask the root interior and set the image background to black")
("--blur_detection", type=str2bool, nargs='?', const=True, default=False, help="whether to omit blurry images")
("--gamma_correction", type=str2bool, nargs='?', const=True, default=False, help="whether to apply gamma correction")
("-g", "--gpus", type=int, default=0, help="how many GPUs to use (set to 0 for CPUs-only)")
("-d", "--dense_strategy", required=False, type=str, default='PMVS', help="whether to use PMVS or COLMAP for dense reconstruction")
("--cache_size", required=False, type=int, default=32, help="Colmap patch matching cache size")
("--window_step", required=False, type=int, default=2, help="Colmap patch window step size")
("--window_radius", required=False, type=int, default=3, help="Colmap patch window radius")
("--num_iterations", required=False, type=int, default=3, help="Colmap patch match iterations")
("--num_samples", required=False, type=int, default=10, help="Colmap patch match sampled views")
("--geom_consistency", required=False, type=str2bool, nargs='?', const=True, default=False, help="Colmap geometric reconstruction")
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
from model_preprocess.bbox_seg_mask import mask_segmentation
from model_preprocess.blur_detector_image import detect_blur
from model_preprocess.gamma_correct import correct_gamma


def reconstruct(
        input_directory,
        output_directory,
        bounding_box,
        mask_segmentation,
        blur_detection,
        gamma_correction,
        gpus,
        dense_strategy,
        cache_size,
        window_step,
        window_radius,
        num_iterations,
        num_samples,
        geom_consistency):
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
    if bounding_box:
        seg_paths = [join(input_directory, file) for file in listdir(input_directory) if isfile(join(input_directory, file))]
        if len(seg_paths) < 2: raise ValueError("Not enough images (" + str(len(seg_paths)) + ")")

        seg_dir = Path(join(output_directory, 'segmented'))
        seg_dir.mkdir(exist_ok=True)
        seg_args = [(path, seg_dir.absolute()) for path in seg_paths]
        input_directory = str(seg_dir.absolute())

        print("Detecting bounding box and cropping " + str(len(seg_paths)) + " images")
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            pool.starmap(foreground_substractor, seg_args)
    if mask_segmentation:
        pass
    if blur_detection:
        bo_paths = [join(input_directory, file) for file in listdir(input_directory) if isfile(join(input_directory, file))]
        if len(bo_paths) < 2: raise ValueError("Not enough images (" + str(len(bo_paths)) + ")")

        bo_dir = Path(join(output_directory, 'blur_omitted'))
        bo_dir.mkdir(exist_ok=True)
        bo_args = [(path, bo_dir.absolute()) for path in bo_paths]
        input_directory = str(bo_dir.absolute())

        print("Applying blur detection to " + str(len(bo_paths)) + " images")
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            pool.starmap(detect_blur, bo_args)
    if gamma_correction:
        gc_paths = [join(input_directory, file) for file in listdir(input_directory) if isfile(join(input_directory, file))]
        if len(gc_paths) < 2: raise ValueError("Not enough images (" + str(len(gc_paths)) + ")")

        gc_dir = Path(join(output_directory, 'gamma_corrected'))
        gc_dir.mkdir(exist_ok=True)
        gc_args = [(path, gc_dir.absolute()) for path in gc_paths]
        input_directory = str(gc_dir.absolute())

        print("Applying gamma correction to " + str(len(gc_paths)) + " images")
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
    subprocess.run("colmap feature_extractor" + \
                   " --image_path " + input_directory + \
                   " --database_path " + database_path + \
                   ((' --SiftExtraction.gpu_index=' + gpu_index) if gpus else ' --SiftExtraction.use_gpu=0'
                                                                                  # last 2 options prevent memory overconsumption with CPU
                                                                                  # https://colmap.github.io/faq.html#available-functionality-without-gpu-cuda
                                                                                  ' --SiftExtraction.num_threads=2'
                                                                                  ' --SiftExtraction.first_octave 0'), shell=True)

    end = time.time()
    feature_extraction_delta = timedelta(seconds=(end - start))
    print("Feature extraction completed in " + humanize.naturaldelta(feature_extraction_delta) + ", starting feature matching")
    start = time.time()

    # feature matching
    # TODO might need --SiftMatching.max_num_matches as per https://colmap.github.io/faq.html#feature-matching-fails-due-to-illegal-memory-access
    subprocess.run("colmap exhaustive_matcher" + \
                   " --database_path " + database_path + \
                   ((' --SiftMatching.gpu_index=' + gpu_index) if gpus else ' --SiftMatching.use_gpu=0'), shell=True)

    end = time.time()
    feature_matching_delta = timedelta(seconds=(end - start))
    print("Feature matching completed in " + humanize.naturaldelta(feature_matching_delta) + ", building sparse model")
    start = time.time()

    # build sparse model
    outer_sparse_dir = Path(join(output_directory, 'sparse'))
    outer_sparse_dir.mkdir(exist_ok=True)
    inner_sparse_dir_path = join(output_directory, 'sparse', '0')
    sparse_model_path = join(output_directory, 'sparse.ply')
    subprocess.run("colmap mapper" + \
                   " --database_path " + database_path + \
                   " --image_path " + input_directory + \
                   " --output_path " + join(outer_sparse_dir.parent.stem, outer_sparse_dir.stem), shell=True)
    subprocess.run("colmap model_converter" + \
                   " --input_path " + inner_sparse_dir_path + \
                   " --output_path " + sparse_model_path + \
                   " --output_type PLY", shell=True)

    end = time.time()
    sparse_model_delta = timedelta(seconds=(end - start))
    print("Sparse model completed in " + humanize.naturaldelta(sparse_model_delta) + ", building dense model")
    start = time.time()

    dense_dir = Path(join(output_directory, 'dense'))
    dense_dir.mkdir(exist_ok=True)
    dense_dir_path = str(dense_dir.absolute())

    # image undistortion
    subprocess.run("colmap image_undistorter" + \
                   " --image_path " + input_directory + \
                   " --input_path " + inner_sparse_dir_path + \
                   " --output_path " + dense_dir_path + \
                   " --output_type " + dense_strategy + \
                   " --max_image_size 2000", shell=True)

    # build dense model
    if gpus and dense_strategy == 'COLMAP':
        # patch match
        subprocess.run("colmap patch_match_stereo" + \
                       " --workspace_path " + dense_dir_path + \
                       " --workspace_format COLMAP" + \
                       " --PatchMatchStereo.cache_size=" + str(cache_size) + \
                       " --PatchMatchStereo.window_step=" + str(window_step) + \
                       " --PatchMatchStereo.window_radius=" + str(window_radius) + \
                       " --PatchMatchStereo.num_iterations=" + str(num_iterations) + \
                       " --PatchMatchStereo.num_samples=" + str(num_samples) + \
                       " --PatchMatchStereo.geom_consistency " + str('true' if geom_consistency else 'false') + \
                       " --PatchMatchStereo.filter " + str('false' if geom_consistency else 'true') + \
                       str((' --PatchMatchStereo.gpu_index=' + gpu_index) if gpus else ''), shell=True)

        # stereo fusion
        dense_model_path = join(output_directory, 'dense.ply')
        subprocess.run("colmap stereo_fusion" + \
                       " --workspace_path " + dense_dir_path + \
                       " --workspace_format COLMAP" + \
                       " --input_type " + str('geometric' if geom_consistency else 'photometric') + \
                       " --output_path " + dense_model_path, shell=True)

        # generate mesh
        mesh_model_path = join(output_directory, 'mesh.ply')
        subprocess.run("colmap poisson_mesher" + \
                       " --input_path " + dense_model_path + \
                       " --output_path " + mesh_model_path, shell=True)
    else:
        if dense_strategy == 'COLMAP':
            print("COLMAP dense reconstruction only supported on GPU hardware")

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
    ap.add_argument("--bounding_box", type=str2bool, nargs='?', const=True, default=False, help="whether to detect the root boundary and crop to a bounding box")
    ap.add_argument("--mask_segmentation", type=str2bool, nargs='?', const=True, default=False, help="whether to segment and mask the root interior and set the image background to black")
    ap.add_argument("--blur_detection", type=str2bool, nargs='?', const=True, default=False, help="whether to omit blurry images")
    ap.add_argument("--gamma_correction", type=str2bool, nargs='?', const=True, default=False, help="whether to apply gamma correction")
    ap.add_argument("-g", "--gpus", type=int, default=0, help="how many GPUs to use (set to 0 for CPUs-only)")
    ap.add_argument("-d", "--dense_strategy", required=False, type=str, default='PMVS', help="whether to use PMVS or COLMAP for dense reconstruction")
    ap.add_argument("--cache_size", required=False, type=int, default=32, help="Colmap patch matching cache size")
    ap.add_argument("--window_step", required=False, type=int, default=2, help="Colmap patch window step size")
    ap.add_argument("--window_radius", required=False, type=int, default=3, help="Colmap patch window radius")
    ap.add_argument("--num_iterations", required=False, type=int, default=3, help="Colmap patch match iterations")
    ap.add_argument("--num_samples", required=False, type=int, default=10, help="Colmap patch match sampled views")
    ap.add_argument("--geom_consistency", type=str2bool, nargs='?', const=True, default=False, help="Colmap geometric reconstruction")
    args = vars(ap.parse_args())

    dense_strategy = args["dense_strategy"]
    if dense_strategy != 'PMVS' and dense_strategy != 'COLMAP':
        raise ValueError("Dense reconstruction strategy must be either PMVS or COLMAP")

    reconstruct(
        input_directory=args["input_directory"],
        output_directory=args["output_directory"],
        bounding_box=bool(args["bounding_box"]),
        mask_segmentation=bool(args['mask_segmentation']),
        blur_detection=bool(args["blur_detection"]),
        gamma_correction=bool(args["gamma_correction"]),
        gpus=int(args["gpus"]),
        dense_strategy=dense_strategy,
        cache_size=int(args["cache_size"]),
        window_step=int(args["window_step"]),
        window_radius=int(args["window_radius"]),
        num_iterations=int(args["num_iterations"]),
        num_samples=int(args["num_samples"]),
        geom_consistency=bool(args["geom_consistency"]))
