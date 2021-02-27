#!/bin/bash

python3.8 cli.py "$1"
find "$1" -name "*.ply" -exec mv '{}' . \;
