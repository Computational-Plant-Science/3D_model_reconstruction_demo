# SFM for 3D root model reconstructure 

## Build requirements
GTK toolkit development files, freeglut development files, libdevil development
files. Install all dependencies in Debian GNU/Linux with `make install-reqs`.

## Usage

./vsfm-master/vsfm/bin/VisualSFM sfm+pairs /home/suxingliu/Root_image_data/3600_10_whole/PairList_90_2.txt 

./vsfm-master/vsfm/bin/VisualSFM sfm+pmvs /home/suxingliu/Tree

## Author
suxing liu(suxingliu@gmail.com)
reference:
[Anders Damsgaard](mailto:adamsgaard@ucsd.edu) with contributions by Caleb Adams 
and Connor P Doherty.
Changchang Wu ( wucc1130@gmail.com ) 

## Todo
- VisualSFM is built without CUDA acceleration. Add optional GPU build.
- Add support for CMVS/PMVS2

## License
GNU Public License
