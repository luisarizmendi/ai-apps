import streamlit as st
import cv2
import requests
import base64
import time
from PIL import Image
import io

# Function to capture and send frames to the model
def capture_and_send_frame():
    global is_running, frame_count, inference_count
    frame_count = 0  # Reset frame count
    inference_count = 0  # Reset inference count
    
    while is_running:
        cap = None
        while cap is None or not cap.isOpened():
            cap = cv2.VideoCapture(selected_camera)
            if not cap.isOpened():
                time.sleep(1)
        
        ret, frame = cap.read()
        cap.release()
        if not ret:
            break

        # Convert the frame to PIL Image
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Convert frame to bytes and base64 encoding for model
        bytes_io = io.BytesIO()
        img.save(bytes_io, format="JPEG")
        img_bytes = bytes_io.getvalue()
        b64_image = base64.b64encode(img_bytes).decode('utf-8')
        data = {'image': b64_image}

        # Send the image to the model for detection
        frame_count += 1  
        frames_placeholder.text(f"Frames Sent: {frame_count}")
        
        response = requests.post(f'{endpoint}/detection', headers=headers, json=data, verify=False)
        if response.status_code == 200:
            response_json = response.json()
            result_image_b64 = response_json["image"]
            result_image = base64.b64decode(result_image_b64)
            result_window.image(result_image, use_column_width=True)
            
            inference_count += 1  
            inferences_placeholder.text(f"Inferences Processed: {inference_count}")

        time.sleep(interval_ms / 1000) 


# Streamlit configuration
# Default inputs
endpoint = "http://0.0.0.0:8000"
headers = {"accept": "application/json", "Content-Type": "application/json"}

camera_list = []
for i in range(10):  # Check first 10 devices
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        camera_list.append(i)
    cap.release()

col1, col2 = st.columns(2)
with col1:
    selected_camera = st.selectbox("Select Webcam", camera_list)
with col2:
    endpoint = st.text_input("Model Endpoint", endpoint)

interval_ms = st.slider("Capture Interval (milliseconds)", 50, 10000, 5000, step=1)

# Placeholder for result image
result_window = st.image([], use_column_width=True)

# Placeholder for counters
counters_row = st.empty()  
frames_placeholder = st.empty() 
inferences_placeholder = st.empty()  

# Button to start the webcam capture
if st.button("Start"):
    is_running = not 'is_running' in globals() or not is_running  
    if is_running:
        with counters_row.container():
            left_col, right_col = st.columns(2)
            with left_col:
                frames_placeholder.text("Frames Sent: 0")
            with right_col:
                inferences_placeholder.text("Inferences Processed: 0")
        capture_and_send_frame()
