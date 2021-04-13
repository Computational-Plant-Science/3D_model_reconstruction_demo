import os
import subprocess
import time
from datetime import timedelta
from os.path import join

import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument('source')
@click.option('-o', '--output_directory', required=True, type=str, default='')
@click.option('--gpu', required=False, type=bool, default=False)
def reconstruct(source, output_directory, gpu):
    if not os.path.exists(source):
        raise ValueError("Path does not exist!")

    start = time.time()
    database = join(output_directory, 'database.db')

    # feature extraction
    subprocess.run(f"colmap feature_extractor --image_path {source} --database_path {database} --SiftExtraction.use_gpu={gpu} --SiftExtraction.num_threads=2 --SiftExtraction.first_octave 0", shell=True)

    # feature matching
    subprocess.run(f"colmap exhaustive_matcher --database_path {database} --SiftMatching.use_gpu={gpu}", shell=True)

    # sparse model
    sparse = join(output_directory, 'sparse')
    subprocess.run(f"mkdir {sparse}", shell=True)
    subprocess.run(f"colmap mapper --database_path {database} --image_path {source} --output_path {sparse}", shell=True)

    # NVM model
    subprocess.run(f"colmap model_converter --input_path {join(sparse, '0')} --output_path {join(output_directory, 'model.nvm')} --output_type NVM", shell=True)

    # dense model
    subprocess.run(f"/opt/code/vsfm/bin/VisualSFM sfm+loadnvm+pmvs {join(output_directory, 'model.nvm')} {join(output_directory, 'dense.nvm')}", shell=True)

    end = time.time()
    print(f"Finished in {timedelta(seconds=(end - start))}")

    # TODO GPU version
    '''
    subprocess.run(f"mkdir {path}/dense", shell=True)
    subprocess.run(f"colmap image_undistorter --image_path {path} --input_path {path}/sparse/0 --output_path {path}/dense --output_type COLMAP --max_image_size 2000", shell=True)

    # patch match stereo
    subprocess.run(f"colmap patch_match_stereo --workspace_path {path}/dense" + " --workspace_format COLMAP --PatchMatchStereo.geom_consistency true", shell=True)

    # stereo fusion
    subprocess.run(f"colmap stereo_fusion --workspace_path {path}/dense --workspace_format COLMAP --input_type geometric --output_path {path}/dense/fused.ply", shell=True)

    # poisson mesher
    subprocess.run(f"colmap poisson_mesher --input_path {path}/dense/fused.ply --output_path {path}/dense/meshed-poisson.ply", shell=True)
    '''


if __name__ == '__main__':
    cli()
