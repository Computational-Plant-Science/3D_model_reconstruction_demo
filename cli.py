import os
import subprocess

import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument('path')
@click.option('--gpu', required=False, type=bool, default=False)
def run(path, gpu):
    if os.path.exists(path):
        print("Image files path exist...\n")
    else:
        print("Image files path was not valid!\n")

    print(f"Running feature extraction")
    feature_extract = "colmap feature_extractor --image_path " + path + " --database_path " + path + "/database.db " + f"--SiftExtraction.use_gpu={gpu}"
    subprocess.run(feature_extract, shell=True)

    print(f"Running feature matching")
    feature_matching = "colmap exhaustive_matcher --database_path " + path + "/database.db" + " --SiftMatching.use_gpu={gpu}"
    subprocess.run(feature_matching, shell=True)

    create_folder_sparse = "mkdir " + path + "/sparse"
    subprocess.run(create_folder_sparse, shell=True)

    print(f"Running sparse model")
    sparse_model = "colmap mapper --database_path " + path + "/database.db " + "--image_path " + path + " --output_path " + path + "/sparse"
    subprocess.run(sparse_model, shell=True)

    print(f"Running NVM model")
    nvm_model = "colmap model_converter --input_path " + path + "/sparse/0 " + " --output_path " + path + "/model.nvm " + " --output_type NVM"
    subprocess.run(nvm_model, shell=True)

    print(f"Running dense model")
    dense_model = "/opt/code/vsfm/bin/VisualSFM sfm+loadnvm+pmvs " + path + "/model.nvm " + path + "/dense.nvm "
    subprocess.run(dense_model, shell=True)


if __name__ == '__main__':
    cli()
