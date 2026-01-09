from ultralytics import YOLO
import urllib.request
import os

# Descargar imagen de prueba (partido de fútbol)
image_url = "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=1280"
image_path = "test_football.jpg"

if not os.path.exists(image_path):
    print("📥 Descargando imagen de prueba...")
    urllib.request.urlretrieve(image_url, image_path)
    print("✅ Imagen descargada")

# Cargar modelo
model = YOLO('yolov8n.pt')

# Detectar objetos
print("\n🔍 Detectando objetos...")
results = model(image_path)

# Mostrar resultados
result = results[0]
print(f"\n📊 Resultados:")
print(f"   Objetos detectados: {len(result.boxes)}")

# Contar por clase
from collections import Counter
classes = [model.names[int(box.cls)] for box in result.boxes]
counts = Counter(classes)

print(f"\n   Detalle por clase:")
for cls, count in counts.most_common():
    print(f"      - {cls}: {count}")

# Guardar imagen con detecciones
output_path = "test_football_detected.jpg"
result.save(filename=output_path)
print(f"\n✅ Imagen guardada: {output_path}")
print("   Ábrela para ver las detecciones!")