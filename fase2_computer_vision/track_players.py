from ultralytics import YOLO
import supervision as sv
import cv2

# Cargar modelo
model = YOLO('yolov8n.pt')

# Configurar tracker (ByteTrack)
tracker = sv.ByteTrack()

# Configurar anotadores
box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()

# Abrir video
video_path = "football_test.mp4"
cap = cv2.VideoCapture(video_path)

# Obtener propiedades del video
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Configurar salida
output_path = "football_tracked.mp4"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

print(f"🎬 Procesando video con tracking...")
print(f"   Entrada: {video_path}")
print(f"   Salida: {output_path}")

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detectar
    results = model(frame, verbose=False, conf=0.3, classes=[0, 32])[0]
    
    # Convertir a formato Supervision
    detections = sv.Detections.from_ultralytics(results)
    
    # Aplicar tracking (asigna IDs únicos)
    detections = tracker.update_with_detections(detections)
    
    # Crear etiquetas con ID de tracking
    labels = [f"#{tracker_id}" for tracker_id in detections.tracker_id]
    
    # Anotar frame
    frame = box_annotator.annotate(frame, detections=detections)
    frame = label_annotator.annotate(frame, detections=detections, labels=labels)
    
    # Guardar frame
    out.write(frame)
    
    frame_count += 1
    if frame_count % 30 == 0:
        print(f"   Procesados: {frame_count} frames")

cap.release()
out.release()

print(f"\n✅ Video con tracking guardado: {output_path}")
print(f"   Total frames procesados: {frame_count}")