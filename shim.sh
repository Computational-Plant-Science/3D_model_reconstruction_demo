#!/bin/bash

/vsfm/bin/VisualSFM sfm+pmvs "$1" .
mv "$1/*.ply" .
