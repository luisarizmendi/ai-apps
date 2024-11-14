PORT ?= 8000
IMAGE ?= quay.io/luisarizmendi/object_counter:latest

MODEL_NAME ?= facebook/detr-resnet-101
MODELS_DIR := /app/models

include ../../../common/Makefile.common

.PHONY: all
all: build download-model-facebook-detr-resnet-101 run 

.PHONY: download-model-facebook-detr-resnet-101
download-model-facebook-detr-resnet-101:
	cd ./../../../tools/download_models/huggingface && \
	./run.sh

.PHONY: download-model-yolov8
download-model-yolov8:
	cd ./../../../tools/download_models/huggingface && \
	./run.sh Ultralytics/YOLOv8

.PHONY: run
run:
	podman run -it -d -p $(PORT):8000 -v ../../../models/$(MODEL_NAME):$(MODELS_DIR)/$(MODEL_NAME):$(BIND_MOUNT_OPTIONS) -e MODEL_PATH=$(MODELS_DIR)/$(MODEL_NAME) $(IMAGE)
