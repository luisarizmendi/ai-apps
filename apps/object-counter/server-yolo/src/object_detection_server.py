from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from huggingface_hub import snapshot_download
from pydantic import BaseModel
import cv2
import base64
import numpy as np
from PIL import Image
from io import BytesIO
from ultralytics import YOLO
import shutil
import os

app = FastAPI()

model_name = os.getenv("MODEL_NAME", default="Ultralytics/YOLOv8")
model_path = os.getenv("MODEL_PATH", default=f"/app/models/{model_name.lower()}")
model_file = os.getenv("MODEL_FILE", default="yolov8m.pt")

# Load detr model
if not os.path.isfile(f"{model_path}/{model_file}"):
    print("Downloading model")
    snapshot_download(repo_id=model_name,
                    local_dir=f"/tmp/{model_path}",
                    local_dir_use_symlinks=False)
    shutil.copytree(f"/tmp/{model_path}", model_path)

model = YOLO(f"{model_path}/{model_file}")

class ImageData(BaseModel):
    image: str

def decode_base64_image(b64_string):
    img_data = base64.b64decode(b64_string)
    image = Image.open(BytesIO(img_data))
    return np.array(image)

# Helper function to draw rectangles, labels, and count occurrences
def draw_boxes_and_count(image, results):
    entity_count = {}  # Dictionary to count occurrences of each entity
    for result in results:
        # Get bounding box coordinates and class names
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
            class_id = int(box.cls[0])  # Class index
            confidence = box.conf[0]  # Confidence score
            class_name = model.names[class_id]  # Get the class name from YOLO model

            # Increment the entity count for the detected class
            if class_name in entity_count:
                entity_count[class_name] += 1
            else:
                entity_count[class_name] = 1

            # Draw the red rectangle around the object
            cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 1)  

            # Put the class name 
            label = f"{class_name} {confidence:.2f}"
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)  

    # Add the entity counts to the top-left corner of the image
    offset = 20  # Space between lines of text
    for class_name, count in entity_count.items():
        cv2.putText(image, f"{class_name}: {count}", (10, offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        offset += 30  # Move down for the next line

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return image

# Define the /detection endpoint
@app.post("/detection")
async def detect_objects(data: ImageData):
    try:
        # Decode the incoming image
        img = decode_base64_image(data.image)

        # Perform inference
        results = model(img)

        # Process the results (draw bounding boxes, labels, and entity counts)
        result_image = draw_boxes_and_count(img, results)

        # Encode the result image back to base64
        _, img_encoded = cv2.imencode('.jpg', result_image)  # Encode to jpg
        img_b64 = base64.b64encode(img_encoded).decode('utf-8')

        # Return the base64 encoded image with detected results
        return JSONResponse(content={"image": img_b64})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
