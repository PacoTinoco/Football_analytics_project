from ultralytics import YOLO
import supervision as sv
import cv2
import pandas as pd

# Cargar modelo y tracker
model = YOLO('yolov8n.pt')
tracker = sv.ByteTrack()

# Abrir video
video_path = "football_test.mp4"
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)

print(f"🎬 Extrayendo datos de tracking...")

# Almacenar datos
tracking_data = []

frame_num = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detectar
    results = model(frame, verbose=False, conf=0.3, classes=[0, 32])[0]
    detections = sv.Detections.from_ultralytics(results)
    
    # Aplicar tracking
    detections = tracker.update_with_detections(detections)
    
    # Guardar cada detección
    for i in range(len(detections)):
        x1, y1, x2, y2 = detections.xyxy[i]
        tracker_id = detections.tracker_id[i]
        class_id = detections.class_id[i]
        confidence = detections.confidence[i]
        
        tracking_data.append({
            'frame': frame_num,
            'time_sec': round(frame_num / fps, 2),
            'tracker_id': tracker_id,
            'class': model.names[class_id],
            'confidence': round(confidence, 3),
            'center_x': round((x1 + x2) / 2, 1),
            'center_y': round((y1 + y2) / 2, 1)
        })
    
    frame_num += 1
    if frame_num % 100 == 0:
        print(f"   Procesados: {frame_num} frames")

cap.release()

# Crear DataFrame
df = pd.DataFrame(tracking_data)
df.to_csv('tracking_data.csv', index=False)

print(f"\n✅ Datos guardados: tracking_data.csv")
print(f"\n📊 Resumen:")
print(f"   Total detecciones: {len(df)}")
print(f"   Jugadores únicos (IDs): {df[df['class']=='person']['tracker_id'].nunique()}")
print(f"   Frames procesados: {df['frame'].nunique()}")

# Mostrar ejemplo
print(f"\n📋 Ejemplo de datos:")
print(df.head(10).to_string(index=False))