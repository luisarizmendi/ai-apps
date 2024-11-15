# Object_Detection_Python Model Server

Currently, the server only implements a single endpoint, `/detection`, that expects an image in bytes and returns an image with labeled bounding boxes and the probability scores of each bounding box. 

## Build Model Server

To build the object_detection_python model server image from this directory:

```bash
podman build -t object_detection_python . base/Containerfile
```
or
```bash
make build
```

## Download Model(s)

You can download models from [huggingface.co](https://huggingface.co/) for this model server. This model server is intended to be used with "DEtection TRansformer" (detr) models. The default model we've used and validated is `ultralytics/yolov8`.

You can download a copy of this model into your `models/` with the make command below. 

```bash
 make download-model
```
or any model with the `download_models` script that you can find in `tools`.

## Deploy Model Server

The model server relies on a volume mount to the localhost to access the model files. It also employs environment variables to dictate the model used and where its served. 

You can start your model server using the following `make` command:

```bash
make run
```

> **Note:**
> It takes some time to start, check the container logs until you see "Started server process"


or if you want to run it manually:

```bash
podman run -it -d -p 8001:8000 \
-v ../../../models/ultralytics/yolov8:/app/models/ultralytics/yolov8:Z,ro \
-e MODEL_PATH=/app/models/ultralytics/yolov8 \
$IMAGE
```

> **Note:**
> You have an image ready in `quay.io/luisarizmendi/object_counter:yolo`

or just:

```bash
podman run -it -d -p 8001:8000 $IMAGE
```

> **Note:**
> If you don't have the model downloaded, you don't need to mount the directory, the container will download the model (`yolov8`) for you, but it will take more time to start...

## Clean container

```bash
make podman-clean
```