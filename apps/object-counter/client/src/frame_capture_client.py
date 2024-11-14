import streamlit as st
import cv2
import requests
import base64
import time
from PIL import Image
import io

# Function to capture and send frames to the model
def capture_and_send_frame():
    global is_running  # Flag to control Start/Stop functionality
    while is_running:
        # Reinitialize the VideoCapture object each iteration to ensure a fresh frame
        cap = cv2.VideoCapture(selected_camera)
        ret, frame = cap.read()
        cap.release()  # Release immediately after capturing the frame
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
        response = requests.post(f'{endpoint}/detection', headers=headers, json=data, verify=False)
        if response.status_code == 200:
            response_json = response.json()
            result_image_b64 = response_json["image"]
            result_image = base64.b64decode(result_image_b64)
            result_window.image(result_image, use_column_width=True)
        
        time.sleep(interval)  # Wait for the next snapshot


# Streamlit configuration
#st.title("Webcam frame capture client")

# Default inputs
endpoint = "http://0.0.0.0:8000"
headers = {"accept": "application/json", "Content-Type": "application/json"}

camera_list = []
for i in range(10):  # Check first 5 devices
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        camera_list.append(i)
    cap.release()
selected_camera = st.selectbox("Select Webcam", camera_list)

# Manual input for the endpoint
endpoint = st.text_input("Model Endpoint", endpoint)

# Configure interval time for capturing
interval = st.slider("Capture Interval (seconds)", 1, 10, 5)

# Placeholder for result image
result_window = st.image([], use_column_width=True)

# Button to start the webcam capture
if st.button("Start"):
    is_running = not 'is_running' in globals() or not is_running  # Toggle the flag
    if is_running:
        capture_and_send_frame()
