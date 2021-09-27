#!/bin/bash

colmap feature_extractor --image_path $INPUT --database_path $OUTPUT/database.db
colmap exhaustive_matcher --database_path $OUTPUT/database.db
colmap mapper --image_path $INPUT --database_path $OUTPUT/database.db --output_path $OUTPUT
colmap model_converter --input_path $OUTPUT/0 --output_path $OUTPUT/model.ply --output_type PLY
