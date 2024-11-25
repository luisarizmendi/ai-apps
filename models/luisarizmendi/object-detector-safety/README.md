
# Model for safety-equipment detection


<div align="center">
  <img width="640" alt="luisarizmendi/safety-equipment" src="https://huggingface.co/luisarizmendi/yolo11-safety-equipment/resolve/main/example.png">
</div>

## Model binary

You can [download the model from here](https://github.com/luisarizmendi/ai-apps/raw/refs/heads/main/models/luisarizmendi/object-detector-safety/object-detector-safety-v1.pt)


## Labels

```
- glove
- goggles
- helmet
- mask
- no_glove
- no_goggles
- no_helmet
- no_mask
- no_shoes
- shoes
```


## Model metrics


<div align="center">
  <img width="640" alt="luisarizmendi/safety-equipment" src="https://huggingface.co/luisarizmendi/yolo11-safety-equipment/resolve/main/confusion_matrix_normalized.png"> <img width="640" alt="luisarizmendi/safety-equipment" src="https://huggingface.co/luisarizmendi/yolo11-safety-equipment/resolve/main/results.png">
</div>


## Model Dataset

[https://universe.roboflow.com/luisarizmendi/safety-or-hat/dataset/1](https://universe.roboflow.com/personal-protective-equipment/ppes-kaxsi)

This dataset is based on [this other one that you can find in Roboflow](https://universe.roboflow.com/luisarizmendi/safety-or-hat/dataset/1?ref=roboflow2huggingface)


## Model training

You can [review the Jupyter notebook here](https://github.com/luisarizmendi/ai-apps/blob/main/dev/safety-hat/train.ipynb)

### Hyperparameters

```
epochs: 35
batch: 2
imgsz: 640
patience: 5
optimizer: 'SGD'
lr0: 0.001
lrf: 0.01
momentum: 0.9
weight_decay: 0.0005
warmup_epochs: 3
warmup_bias_lr: 0.01
warmup_momentum: 0.8
```

### Augmentation

```
hsv_h=0.015,  # Image HSV-Hue augmentationc
hsv_s=0.7,   # Image HSV-Saturation augmentation
hsv_v=0.4,   # Image HSV-Value augmentation
degrees=10,  # Image rotation (+/- deg)
translate=0.1,  # Image translation (+/- fraction)
scale=0.3,   # Image scale (+/- gain)
shear=0.0,   # Image shear (+/- deg)
perspective=0.0,  # Image perspective
flipud=0.1,  # Image flip up-down
fliplr=0.1,  # Image flip left-right
mosaic=1.0,  # Image mosaic
mixup=0.0,   # Image mixup
```


## Model Usage


### Usage with Huggingface spaces

If you don't want to run it locally, you can use [this huggingface space](https://huggingface.co/spaces/luisarizmendi/safety-equipment-object-detection) that I've created with this code but be aware that this will be slow since I'm using a free instance, so it's better to run it locally with the python script below.


<div align="center">
  <img width="640" alt="luisarizmendi/safety-equipment" src="https://huggingface.co/luisarizmendi/yolo11-safety-equipment/resolve/main/spaces-example.png">
</div>


### Usage with Python script

Install the following PIP requirements

```
gradio
ultralytics
Pillow
opencv-python
torch
```

Then [run the python code below ](https://huggingface.co/luisarizmendi/yolo11-safety-equipment/blob/main/run_model.py) and open `http://localhost:7860` in a browser to upload and scan the images.


```
import gradio as gr
from ultralytics import YOLO
from PIL import Image
import os
import cv2 
import torch 

def detect_objects_in_files(files):
    """
    Processes uploaded images for object detection.
    """
    if not files:
        return "No files uploaded.", []

    device = "cuda" if torch.cuda.is_available() else "cpu"  
    model = YOLO("https://github.com/luisarizmendi/ai-apps/raw/refs/heads/main/models/luisarizmendi/object-detector-safety/object-detector-safety-v1.pt")
    model.to(device)
    
    results_images = []
    for file in files:
        try:
            image = Image.open(file).convert("RGB")
            results = model(image) 
            result_img_bgr = results[0].plot()
            result_img_rgb = cv2.cvtColor(result_img_bgr, cv2.COLOR_BGR2RGB)
            results_images.append(result_img_rgb)   
         
            # If you want that images appear one by one (slower)
            #yield "Processing image...", results_images  
                
        except Exception as e:
            return f"Error processing file: {file}. Exception: {str(e)}", []

    del model  
    torch.cuda.empty_cache()
    
    return "Processing completed.", results_images

interface = gr.Interface(
    fn=detect_objects_in_files,
    inputs=gr.Files(file_types=["image"], label="Select Images"),
    outputs=[
        gr.Textbox(label="Status"),
        gr.Gallery(label="Results")
    ],
    title="Object Detection on Images",
    description="Upload images to perform object detection. The model will process each image and display the results."
)

if __name__ == "__main__":
    interface.launch()
```




