from ultralytics import YOLO
import cv2

# Cargar modelo
model = YOLO('yolov8n.pt')

# Rutas
video_path = "football_test.mp4"
output_path = "football_detected.mp4"

# Procesar video
print("🎬 Procesando video con YOLO...")
print("   (Esto puede tomar 1-3 minutos)\n")

results = model(
    source=video_path,
    save=True,
    conf=0.3,  # Confianza mínima 30%
    classes=[0, 32],  # 0=person, 32=sports ball
    project=".",
    name="output"
)

print("\n✅ Video procesado!")
print("   Busca la carpeta 'output' - ahí está el video con detecciones")