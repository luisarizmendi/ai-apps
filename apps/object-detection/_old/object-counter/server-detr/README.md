# Object_Detection_Python Model Server

The object_detection_python model server is a simple [FastAPI](https://fastapi.tiangolo.com/) application written specifically for use in the [object_detection recipe](../../recipes/computer_vision/object_detection/) with "DEtection TRansformer" (DETR) models.  It relies on huggingface's transformer package for `AutoImageProcessor` and `AutoModelforObjectDetection` to process image data and to make inferences respectively.

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

You can download models from [huggingface.co](https://huggingface.co/) for this model server. This model server is intended to be used with "DEtection TRansformer" (detr) models. The default model we've used and validated is [facebook/detr-resnet-101](https://huggingface.co/facebook/detr-resnet-101).

You can download a copy of this model into your `models/` with the make command below. 

```bash
 make download-model-facebook-detr-resnet-101
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
podman run -it -d -p 8000:8000 \
-v ../../../models/facebook/detr-resnet-101:/app/models/facebook/detr-resnet-101:Z,ro \
-e MODEL_PATH=/app/models/facebook/detr-resnet-101 \
$IMAGE
```

> **Note:**
> You have an image ready to be used in `quay.io/luisarizmendi/object_counter:detr`

If you don't have the `DETR` model of your choose downloaded, you don't need to mount the directory, the container will download the model that you select by configuring the `MODEL_NAME` with the Huggingface model name that you want to use (defaults to `facebook-detr-resnet-101`). It will take more time to start comparing with a pre-downloaded model (check logs and wait until the download is finised to use the inference service):

You can also choose the model filename/size by configuring the `MODEL_FILE` variable (defaults to `pytorch_model.bin`)

```bash
podman run -it -d -p 8000:8000 -e MODEL_NAME=facebook/detr-resnet-50  $IMAGE
```

## Clean container

```bash
make podman-clean
```