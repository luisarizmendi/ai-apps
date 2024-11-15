import streamlit as st
import cv2
import requests
import base64
import time
from PIL import Image
import io

# Funciones y variables globales
is_running = False
frames_sent = 0
frames_processed = 0
start_time = None
total_processing_time = 0

# Función para capturar y enviar el frame
def capture_and_send_frame():
    global is_running, frames_sent, frames_processed, start_time, total_processing_time
    if start_time is None:
        start_time = time.time()
        
    while is_running:
        cap = cv2.VideoCapture(selected_camera)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            break

        frames_sent += 1
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        bytes_io = io.BytesIO()
        img.save(bytes_io, format="JPEG")
        img_bytes = bytes_io.getvalue()
        b64_image = base64.b64encode(img_bytes).decode('utf-8')
        data = {'image': b64_image}

        request_start = time.time()
        response = requests.post(f'{endpoint}/detection', headers=headers, json=data, verify=False)
        processing_time = time.time() - request_start
        total_processing_time += processing_time

        if response.status_code == 200:
            frames_processed += 1
            response_json = response.json()
            result_image_b64 = response_json["image"]
            result_image = base64.b64decode(result_image_b64)
            result_window.image(result_image, use_column_width=True)
        
        # Actualización dinámica de métricas
        frames_sent_placeholder.markdown(f"**Frames**: {frames_sent}")
        elapsed_time = time.time() - start_time
        avg_fps_sent = frames_sent / elapsed_time
        avg_fps_received = frames_processed / elapsed_time if frames_processed else 0
        avg_inference_time = total_processing_time / frames_processed if frames_processed else 0
        avg_fps_sent_placeholder.markdown(f"**Avg FPS**: {avg_fps_sent:.2f}")
        elapsed_time_placeholder.markdown(f"**Elapsed Time**: {elapsed_time:.2f}s")
        avg_inference_time_placeholder.markdown(f"**Avg Inference Time**: {avg_inference_time:.2f}s")

        time.sleep(1 / fps)  # Control de la frecuencia de captura

# Configuración de Streamlit sin título
col_camera, col_endpoint = st.columns(2)
with col_camera:
    selected_camera = st.selectbox("Select Webcam", [i for i in range(10) if cv2.VideoCapture(i).isOpened()])
with col_endpoint:
    endpoint = st.text_input("Model Endpoint", "http://0.0.0.0:8000")

headers = {"accept": "application/json", "Content-Type": "application/json"}
fps = st.slider("Capture Rate (FPS)", min_value=0.01, max_value=10.0, value=0.2, step=0.01)

# Placeholder para mostrar resultados
result_window = st.image([])

# Placeholders para estadísticas (organizadas en filas y columnas)
stats_container = st.container()
with stats_container:
    col1, col2 = st.columns(2)
    avg_fps_sent_placeholder = col1.markdown("**Avg FPS**: 0.00")
    frames_sent_placeholder = col2.markdown("**Frames**: 0")

    col3, col4 = st.columns(2)
    elapsed_time_placeholder = col3.markdown("**Elapsed Time**: 0.00s")
    avg_inference_time_placeholder = col4.markdown("**Avg Inference Time**: 0.00s")


# Botón para iniciar y detener
if st.button("Start"):
    is_running = not is_running
    if is_running:
        frames_sent = frames_processed = 0
        start_time = None
        total_processing_time = 0
        capture_and_send_frame()
