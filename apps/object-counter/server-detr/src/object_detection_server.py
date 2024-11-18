from transformers import AutoImageProcessor, AutoModelForObjectDetection
from huggingface_hub import snapshot_download
from PIL import Image, ImageDraw, ImageFont
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

# Model configuration from environment variables
model_name = os.getenv("MODEL_NAME", default="facebook/detr-resnet-101")
model_path = os.getenv("MODEL_PATH", default=f"/app/models/{model_name.lower()}")
model_file = os.getenv("MODEL_FILE", default="pytorch_model.bin")
revision = os.getenv("MODEL_REVISION", default="no_timm")

# Device configuration (use GPU if available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model and processor
if not os.path.isfile(f"{model_path}/{model_file}"):  
    print("Downloading model")
    snapshot_download(repo_id=model_name,
                    revision=revision,
                    local_dir=f"/tmp/{model_path}",
                    local_dir_use_symlinks=False)
    shutil.copytree(f"/tmp/{model_path}", model_path)

# Load processor and model only once
processor = AutoImageProcessor.from_pretrained(model_path, revision=revision)
model = AutoModelForObjectDetection.from_pretrained(model_path, revision=revision).to(device)


# Define the input model for the image
class Item(BaseModel):
    image: str  # Changed to string for easier base64 handling

@app.get("/health")
def tests_alive():
    return {"alive": True}

@app.post("/detection")
def detection(item: Item):
    try:
        # Decode the base64 image to a PIL image
        b64_image = item.image
        b64_image = base64.b64decode(b64_image)
        bytes_io = io.BytesIO(b64_image)    
        image = Image.open(bytes_io)

        # Detection for detr
        inputs = processor(images=image, return_tensors="pt").to(device)  # Move to device (GPU or CPU)
        outputs = model(**inputs)
        target_sizes = torch.tensor([image.size[::-1]]).to(device)  # Target sizes should be on the same device
        results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

        # Drawing on image and preparing results
        draw = ImageDraw.Draw(image)
        scores = []
        entity_counts = defaultdict(int)

        try:
            font = ImageFont.truetype("arialbd.ttf", 20)  
        except IOError:
            font = ImageFont.load_default() 

        # Loop through detection results and draw bounding boxes and labels
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            entity_name = model.config.id2label[label.item()] 
            entity_counts[entity_name] += 1
            box = [round(i, 2) for i in box.tolist()]
            x, y, x2, y2 = tuple(box)
            
            # Draw bounding box
            draw.rectangle((x, y, x2, y2), outline="red", width=1)
            
            # Draw label with confidence
            label_with_confidence = f"{entity_name} {round(score.item(), 2)}"
            draw.text((x, y), label_with_confidence, fill="red", font=font)
            
            label_confidence = f"Detected {entity_name} with confidence {round(score.item(), 3)}"
            scores.append(label_confidence)
        
        # Draw entity counts
        y_offset = 10
        for entity_name, count in entity_counts.items():
            draw.text((10, y_offset), f"{entity_name}: {count}", fill="red", font=font)
            y_offset += 25

        # Convert the image to base64 for the response
        bytes_io = io.BytesIO() 
        image.save(bytes_io, "JPEG")
        img_bytes = bytes_io.getvalue()
        img_bytes = base64.b64encode(img_bytes).decode('utf-8')
        
        # Return the image and bounding box scores
        return {'image': img_bytes, "boxes": scores}

    except Exception as e:
        logging.error(f"Error during detection: {e}")
        return {"error": str(e)}
