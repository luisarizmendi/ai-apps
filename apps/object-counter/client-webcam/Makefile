PORT ?= 8501
IMAGE ?= quay.io/luisarizmendi/frame_capture_client:latest

include ../../../common/Makefile.common

.PHONY: run
run:
	CMD="podman run -d -p $(PORT):8500 --privileged --network host "; \
	for device in /dev/video*; do \
		if [ -e "$device" ]; then \
			CMD="$$CMD --device=$$device:$$device"; \
		fi; \
	done; \
	CMD="$$CMD $(IMAGE)"; \
	eval $$CMD



