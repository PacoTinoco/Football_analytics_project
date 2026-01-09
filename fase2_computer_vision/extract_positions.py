from ultralytics import YOLO
import cv2
import pandas as pd

# Cargar modelo
model = YOLO('yolov8n.pt')
video_path = "football_test.mp4"

# Abrir video
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"📹 Video: {video_path}")
print(f"   FPS: {fps}")
print(f"   Frames totales: {total_frames}")
print(f"   Duración: {total_frames/fps:.1f} segundos")

# Almacenar detecciones
all_detections = []

print(f"\n🔍 Extrayendo posiciones...")

frame_num = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detectar cada 5 frames (para ir más rápido)
    if frame_num % 5 == 0:
        results = model(frame, verbose=False, conf=0.3, classes=[0, 32])
        
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            confidence = box.conf[0].item()
            class_id = int(box.cls[0].item())
            class_name = model.names[class_id]
            
            # Calcular centro del objeto
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            all_detections.append({
                'frame': frame_num,
                'time_sec': frame_num / fps,
                'class': class_name,
                'confidence': round(confidence, 3),
                'center_x': round(center_x, 1),
                'center_y': round(center_y, 1),
                'width': round(x2 - x1, 1),
                'height': round(y2 - y1, 1)
            })
    
    frame_num += 1
    
    # Mostrar progreso
    if frame_num % 50 == 0:
        print(f"   Procesado: {frame_num}/{total_frames} frames")

cap.release()

# Crear DataFrame
df = pd.DataFrame(all_detections)

print(f"\n📊 Resultados:")
print(f"   Detecciones totales: {len(df)}")
print(f"   Personas detectadas: {len(df[df['class'] == 'person'])}")
print(f"   Balones detectados: {len(df[df['class'] == 'sports ball'])}")

# Guardar a CSV
df.to_csv('detections.csv', index=False)
print(f"\n✅ Datos guardados en: detections.csv")

# Mostrar primeras filas
print(f"\n📋 Primeras detecciones:")
print(df.head(10).to_string(index=False))