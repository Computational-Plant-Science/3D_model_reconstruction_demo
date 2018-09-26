# VisualSFM builder for Linux (64 bit)

## Build requirements
GTK toolkit development files, freeglut development files, libdevil development
files. Install all dependencies in Debian GNU/Linux with `make install-reqs`.

## Usage
This script installs, builds and runs VisualSFM and its requirements SiftGPU
and PBA in the directory. Simply execute `./visualsfm.sh`. On the first run it
will download, install, build and run the software. Subsequent runs of 
`./visualsfm.sh` launch the VisualSFM GUI.

## Author
[Anders Damsgaard](mailto:adamsgaard@ucsd.edu) with contributions by Caleb Adams 
and Connor P Doherty.

## Todo
- VisualSFM is built without CUDA acceleration. Add optional GPU build.
- Add support for CMVS/PMVS2

## License
GNU Public License, v. 3. See ``LICENSE.txt`` for details.
