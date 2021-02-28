#!/bin/bash
'
Reconstruct 3D root model from image dataset using colmap and SFM.
'


colmap feature_extractor --image_path /images/ --database_path /images/database.db --SiftExtraction.use_gpu=false

colmap exhaustive_matcher --database_path /images/database.db --SiftMatching.use_gpu=false

mkdir /images/sparse

colmap mapper --database_path /images/database.db --image_path /images/ --output_path /images/sparse/

colmap model_converter --input_path /images/sparse/0 --output_path /images/model.nvm --output_type NVM

/opt/code/vsfm/bin/VisualSFM sfm+loadnvm+pmvs /images/model.nvm /images/dense.nvm

chmod 777 -R /images/

'
#!/bin/bash
# progress bar function
prog() {
    local w=80 p=$1;  shift
    # create a string of spaces, then change them to dots
    printf -v dots "%*s" "$(( $p*$w/100 ))" ""; dots=${dots// /.};
    # print those dots on a fixed-width space plus the percentage etc. 
    printf "\r\e[K|%-*s| %3d %% %s" "$w" "$dots" "$p" "$*"; 
}
# test loop
for x in {1..100} ; do
    prog "$x" still working...
    sleep .1   # do some work here
done ; echo
'
