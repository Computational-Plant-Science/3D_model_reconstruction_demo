import multiprocessing
import os
import subprocess
import time
from datetime import timedelta
from os import listdir
from os.path import join, isfile
import pprint
from pathlib import Path

import click

from model_preprocess.bbox_seg import foreground_substractor
from model_preprocess.blur_detector_image import detect_blur


@click.group()
def cli():
    pass


@cli.command()
@click.argument('source')
@click.option('--output_directory', '-o', required=True, type=str, default='')
@click.option('--preprocess', '-p', required=False, type=bool, default=False)
@click.option('--gpu', '-g', required=False, type=bool, default=False)
def reconstruct(source, output_directory, preprocess, gpu):
    if not os.path.exists(source):
        raise ValueError("Path does not exist!")

    if preprocess:
        paths = [join(source, file) for file in listdir(source) if isfile(join(source, file))]
        print(f"Preprocessing {len(paths)} files:")
        pprint.pprint(paths)
        preprocessed_directory = Path('preprocessed')
        preprocessed_directory.mkdir(exist_ok=True)

        cores = multiprocessing.cpu_count()
        args = [(path, preprocessed_directory.absolute()) for i, path in enumerate(paths)]
        with multiprocessing.Pool(processes=cores) as pool:
            pool.starmap(foreground_substractor, args)
            pool.starmap(detect_blur, args)
    else: preprocessed_directory = None

    start = time.time()
    database = join(output_directory, 'database.db')

    # feature extraction
    # last two options prevent memory overconsumption in CPU mode https://colmap.github.io/faq.html#available-functionality-without-gpu-cuda
    subprocess.run("colmap feature_extractor --image_path " + (source if preprocessed_directory is None else preprocessed_directory.name) + " --database_path " + database + (" --SiftExtraction.use_gpu=0 --SiftExtraction.num_threads=2 --SiftExtraction.first_octave 0" if not gpu else ''), shell=True)

    # feature matching
    # might need to use --SiftMatching.max_num_matches as per https://colmap.github.io/faq.html#feature-matching-fails-due-to-illegal-memory-access
    subprocess.run("colmap exhaustive_matcher --database_path " + database + " --SiftMatching.use_gpu=" + str(gpu), shell=True)

    # build sparse model
    sparse = join(output_directory, 'sparse')
    subprocess.run("mkdir " + sparse, shell=True)
    subprocess.run("colmap mapper --database_path " + database + " --image_path " + (source if preprocessed_directory is None else preprocessed_directory.name) + " --output_path " + sparse, shell=True)

    # convert models
    subprocess.run("colmap model_converter --input_path " + join(sparse, '0') + " --output_path " + join(output_directory, 'model.nvm') + " --output_type NVM", shell=True)
    subprocess.run("colmap model_converter --input_path " + join(sparse, '0') + " --output_path " + join(output_directory, 'model.ply') + " --output_type PLY", shell=True)

    # dense model
    # subprocess.run("/opt/code/vsfm/bin/VisualSFM sfm+loadnvm+pmvs " + join(output_directory, 'model.nvm') + " " + join(output_directory, 'dense.nvm'), shell=True)

    subprocess.run(f"mkdir {join(output_directory, 'dense')}", shell=True)
    subprocess.run(f"colmap image_undistorter --image_path {source} --input_path {join(output_directory, 'sparse', '0')} --output_path {join(output_directory, 'dense')} --output_type COLMAP --max_image_size 2000", shell=True)

    # patch match stereo
    subprocess.run(f"colmap patch_match_stereo --workspace_path {join(output_directory, 'dense')}" + " --workspace_format COLMAP --PatchMatchStereo.geom_consistency true", shell=True)

    # stereo fusion
    subprocess.run(f"colmap stereo_fusion --workspace_path {join(output_directory, 'dense')} --workspace_format COLMAP --input_type geometric --output_path {join(output_directory, 'dense', 'fused.ply')}", shell=True)

    # poisson mesher (only required for mesh, not point cloud)
    # subprocess.run(f"colmap poisson_mesher --input_path {path}/dense/fused.ply --output_path {path}/dense/meshed-poisson.ply", shell=True)

    end = time.time()
    print("Finished in " + str(timedelta(seconds=(end - start))))


if __name__ == '__main__':
    cli()
