#!/bin/bash

podman run -it --rm --net host -e DETECTIONS_ENDPOINT=http://localhost:5000/current_detections -e ALERT_ENDPOINT=http://localhost:5005/alert -e ALIVE_ENDPOINT=http://localhost:5005/alive quay.io/luisarizmendi/object-detection-action:prod


