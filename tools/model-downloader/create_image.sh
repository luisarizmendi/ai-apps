#!/bin/bash

IMAGE=quay.io/luisarizmendi/model-downloader

podman rmi  ${IMAGE}:x86 &>/dev/null
podman rmi  ${IMAGE}:arm &>/dev/null
podman rmi  ${IMAGE}:latest &>/dev/null
podman manifest rm  ${IMAGE}:latest &>/dev/null

podman build --platform linux/amd64 -t ${IMAGE}:x86 .
podman build --platform linux/arm64 -t ${IMAGE}:arm .

podman push ${IMAGE}:x86
podman push ${IMAGE}:arm

podman manifest create ${IMAGE}:latest
podman manifest add ${IMAGE}:latest docker://${IMAGE}:x86
podman manifest add ${IMAGE}:latest docker://${IMAGE}:arm

podman manifest push ${IMAGE}:latest




