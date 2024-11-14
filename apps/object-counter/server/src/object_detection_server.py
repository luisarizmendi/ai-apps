from transformers import AutoImageProcessor, AutoModelForObjectDetection
from huggingface_hub import snapshot_download
from PIL import Image, ImageDraw
from fastapi import FastAPI
from pydantic import BaseModel
import torch
import base64
import os
import io
import shutil
from collections import defaultdict
import logging

app = FastAPI()

model_type = os.getenv("MODEL_TYPE", default="detr")  # "detr" or "yolo"
model = os.getenv("MODEL_PATH", default="/app/models/facebook/detr-resnet-101")
revision = os.getenv("MODEL_REVISION", default="no_timm")
yolo_version = os.getenv("YOLO_VERSION", default="yolov8m")

# Load the model based on the selected type
if model_type == "yolo":
    # Load yolo
    model_path = f"{model}/{yolo_version}.pt"

    # Check if model file exists locally
    if os.path.isfile(model_path):
        logging.info(f"Loading YOLO model from local file: {model_path}")
        model = torch.load(model_path)
    else:
        logging.info(f"Model file not found locally, downloading YOLO model: {model_path}")
        model = torch.hub.load('ultralytics/yolov8', yolo_version, pretrained=True) 

else:
    # Load DETR
    if not os.path.isfile(f"{model}/pytorch_model.bin"):  
        model_name = os.getenv("MODEL_NAME", default="facebook/detr-resnet-101")
        print("Downloading model")
        snapshot_download(repo_id=model_name,
                        revision=revision,
                        local_dir=f"/tmp/{model}",
                        local_dir_use_symlinks=False)
        shutil.copyfile(f"/tmp/{model}/pytorch_model.bin", f"{model}/pytorch_model.bin")

    processor = AutoImageProcessor.from_pretrained(model, revision=revision)
    model = AutoModelForObjectDetection.from_pretrained(model, revision=revision)



class Item(BaseModel):
    image: bytes 

@app.get("/health")
def tests_alive():
    return {"alive": True}

from collections import defaultdict

from PIL import ImageFont

@app.post("/detection")
def detection(item: Item):
    b64_image = item.image
    b64_image = base64.b64decode(b64_image)
    bytes_io = io.BytesIO(b64_image)    
    image = Image.open(bytes_io)

    # Detection for yolo
    if model_type == "yolo":
        processed = model(image)
        results = processed.pandas().xyxy[0]  
    else:
        # Detection for DETR
        inputs = processor(images=image, return_tensors="pt")
        outputs = model(**inputs)
        target_sizes = torch.tensor([image.size[::-1]])
        results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

    draw = ImageDraw.Draw(image)
    scores = []
    entity_counts = defaultdict(int)
    
    try:
        font = ImageFont.truetype("arialbd.ttf", 20)  
    except IOError:
        font = ImageFont.load_default() 

    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        entity_name = model.config.id2label[label.item()]
        entity_counts[entity_name] += 1
        box = [round(i, 2) for i in box.tolist()]
        x, y, x2, y2 = tuple(box)
        draw.rectangle((x, y, x2, y2), outline="red", width=1)
        draw.text((x, y), entity_name, fill="red", font=font)
        label_confidence = f"Detected {entity_name} with confidence {round(score.item(), 3)}"
        scores.append(label_confidence)
    
    y_offset = 10
    for entity_name, count in entity_counts.items():
        draw.text((10, y_offset), f"{entity_name}: {count}", fill="red", font=font)
        y_offset += 25

#    y_offset = 10
#    image_width, _ = image.size
#    for entity_name, count in entity_counts.items():
#        text = f"{entity_name}: {count}"
#        text_width, _ = draw.textsize(text, font=font)
#        draw.text((image_width - text_width - 10, y_offset), text, fill="white", font=font)
#        y_offset += 25

    bytes_io = io.BytesIO() 
    image.save(bytes_io, "JPEG")
    img_bytes = bytes_io.getvalue()
    img_bytes = base64.b64encode(img_bytes).decode('utf-8')
    return {'image': img_bytes, "boxes": scores}

