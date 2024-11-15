import streamlit as st
import cv2
import requests
import base64
import time
from PIL import Image
import io

# Variables globales
is_running = False
frames_sent = 0
inferences_received = 0
total_send_time = 0
total_infer_time = 0
start_time = 0

# Function to capture and send frames to the model
def capture_and_send_frame():
    global is_running, frames_sent, inferences_received, total_send_time, total_infer_time, start_time
    
    start_time = time.time()  # Start timing
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

        # Measure the time taken to send the frame
        send_start = time.time()
        response = requests.post(f'{endpoint}/detection', headers=headers, json=data, verify=False)
        send_time = time.time() - send_start
        total_send_time += send_time  # Update total send time
        frames_sent += 1  # Increment sent frame count

        # Update frames sent in the UI
        frames_sent_placeholder.write(f"Frames Sent: {frames_sent}")

        if response.status_code == 200:
            response_json = response.json()
            result_image_b64 = response_json["image"]
            result_image = base64.b64decode(result_image_b64)
            result_window.image(result_image, use_column_width=True)
            
            # Measure inference time
            infer_time = time.time() - send_start
            total_infer_time += infer_time
            inferences_received += 1  # Increment received inference count
            
            # Update inferences received in the UI
            inferences_received_placeholder.write(f"Inferences Processed: {inferences_received}")

        time.sleep(1 / fps)  # Wait based on the FPS setting

# Streamlit configuration
# st.title("Webcam frame capture client")

# Default inputs
endpoint = "http://0.0.0.0:8000"
headers = {"accept": "application/json", "Content-Type": "application/json"}

camera_list = []
for i in range(10):  # Check first 10 devices
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        camera_list.append(i)
    cap.release()

# Create layout
col1, col2 = st.columns(2)
selected_camera = col1.selectbox("Select Webcam", camera_list)
endpoint = col2.text_input("Model Endpoint", endpoint)

# Slider for FPS
fps = st.slider("Capture Rate (FPS)", min_value=0.2, max_value=24.0, value=12.1, step=0.1)

# Placeholders for stats
frames_sent_placeholder = st.empty()
inferences_received_placeholder = st.empty()

# Second row for average FPS
col3, col4 = st.columns(2)
average_fps_sent_placeholder = col3.empty()
average_fps_received_placeholder = col4.empty()

# Third row for timing stats
col5, col6 = st.columns(2)
elapsed_time_placeholder = col5.empty()
average_infer_time_placeholder = col6.empty()

# Placeholder for result image
result_window = st.image([], use_column_width=True)

# Button to start the webcam capture
if st.button("Start"):
    is_running = not is_running  
    if is_running:
        frames_sent = 0
        inferences_received = 0
        total_send_time = 0
        total_infer_time = 0
        start_time = time.time()
        
        capture_and_send_frame()

while is_running:
    elapsed_time = time.time() - start_time
    avg_fps_sent = frames_sent / elapsed_time if elapsed_time > 0 else 0
    avg_fps_received = inferences_received / elapsed_time if elapsed_time > 0 else 0
    avg_infer_time = (total_infer_time / inferences_received) if inferences_received > 0 else 0

    frames_sent_placeholder.write(f"Frames Sent: {frames_sent}")
    inferences_received_placeholder.write(f"Inferences Processed: {inferences_received}")
    average_fps_sent_placeholder.write(f"Avg FPS Sent: {avg_fps_sent:.2f}")
    average_fps_received_placeholder.write(f"Avg FPS Received: {avg_fps_received:.2f}")
    elapsed_time_placeholder.write(f"Elapsed Time: {elapsed_time:.2f} s")
    average_infer_time_placeholder.write(f"Avg Inference Time: {avg_infer_time:.2f} s")

    time.sleep(0.1)
