# Client to frame capture and send to model

## Description

Web application that takes frames from a video input (webcam) and send them into the model endpoint.

## Usage

Choose the port and the video devices that you want to use. Check this example using the local port `8501` and `video3` device:

```bash
podman run -d -p 8501:8500 --privileged --network host --device=/dev/video3:/dev/video3 $IMAGE
```

> **Note:**
> You have an image ready in `quay.io/luisarizmendi/frame_capture_client:latest`



## Build and run with Make

#### Build Container image

```bash
make build
```

#### Run Container

```bash
make run
```

> **Note:**
> Defaults to port `8501`

Use the UI to select the IP and port where you want to send your images to perform the object recognition. You can open multiple client UIs sending to different inference endpoints using the same webcam, so you can potentially compare models performance easily.

#### Clean container

```bash
make podman-clean
```