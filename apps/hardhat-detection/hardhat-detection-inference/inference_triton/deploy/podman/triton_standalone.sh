#!/bin/bash

podman run -it --rm --volume /tmp/models:/mnt/models:z \
            --mount type=tmpfs,destination=/dev/shm \
            --security-opt=label=disable --device nvidia.com/gpu=all \
            -e PORT=8000 \
            -e PORT=8001 \
            nvcr.io/nvidia/tritonserver:25.03-py3 \
            /bin/sh -c 'exec tritonserver "--model-repository=/mnt/models" "--allow-http=true" "--allow-sagemaker=false"'


