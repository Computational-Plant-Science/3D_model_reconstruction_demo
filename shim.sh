#!/bin/bash

/vsfm/bin/VisualSFM sfm+pmvs "$1" .
find "$1" -name "*.ply" -exec mv '{}' . \;
