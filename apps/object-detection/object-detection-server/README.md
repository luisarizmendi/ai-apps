# Object detection server

## Description

Python server that uses a YOLO model to provide object detection on a directly connected webcam stream or a batch file upload providing an output stream with the labeled images and the number of detected objects.

## Enpoints

`http://<ip>:5000/video_feed`

Provides the labeled stream from the webcam input stream.


`http://<ip>:5000/current_counts`

Provides the entities detected and the number of each one in that moment


`http://<ip>:5000/detect_image`

Label the uploaded an image. You have an example script using `curl` under the `test` directory.



## Run

Container will need a port and a video input device.

```bash
podman run -d -p 5000:5000 --device=/dev/video1:/dev/video1 quay.io/luisarizmendi/object-detection-server:latest
```


You can also pass all the available devices in your device to the Container by running this script:

```bash
#!/bin/bash

IMAGE="quay.io/luisarizmendi/object-detection-server:latest"
PORT=5000


CMD="podman run -d -p $PORT:$PORT " 

for device in /dev/video*; do 
	if [ -e "$device" ]; then 
		CMD="$CMD --device=$device:$device"
	fi; 
done; 

CMD="$CMD $IMAGE"

echo "Running $CMD"
$($CMD)
```

> **Note:**
> You can select the device to be used by setting the environment variable `CAMERA_INDEX`.


## Build


```bash
podman build -t quay.io/luisarizmendi/object-detection-server:latest .
```