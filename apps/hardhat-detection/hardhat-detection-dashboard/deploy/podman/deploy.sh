#!/bin/bash

podman run -it --rm --net host quay.io/luisarizmendi/object-detection-dashboard-backend:v1


podman run -it --rm --net host -e BACKEND_API_BASE_URL=http://localhost:5005 quay.io/luisarizmendi/object-detection-dashboard-frontend:v1

