# test_yolo.py
from ultralytics import YOLO

# Descargar modelo pre-entrenado (esto descarga ~50MB la primera vez)
model = YOLO('yolov8n.pt')  # 'n' = nano, el más pequeño y rápido

print("✅ YOLO instalado correctamente")
print(f"   Modelo: YOLOv8 nano")
print(f"   Clases que detecta: {len(model.names)}")
print(f"   Algunas clases: {list(model.names.values())[:10]}")