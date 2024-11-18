PORT ?= 8000
IMAGE ?= quay.io/luisarizmendi/object_counter:yolo

MODEL_NAME ?= ultralytics/yolov8
MODELS_DIR := /app/models

include ../../../common/Makefile.common

.PHONY: all
all: build download-model run 

.PHONY: download-model
download-model:
	cd ./../../../tools/download_models/huggingface && \
	./run.sh Ultralytics/YOLOv8

.PHONY: run-
run:
	podman run -it -d -p $(PORT):8000 -v ../../../models/$(MODEL_NAME):$(MODELS_DIR)/$(MODEL_NAME):$(BIND_MOUNT_OPTIONS) -e MODEL_PATH=$(MODELS_DIR)/$(MODEL_NAME) $(IMAGE)
