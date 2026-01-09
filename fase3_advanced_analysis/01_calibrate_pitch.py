"""
Script para calibrar la transformación pixel -> cancha.
Permite seleccionar puntos de referencia en el video.
"""

import cv2
import sys
sys.path.append('src')
from pitch_transform import PitchTransformer
import json

# Ruta al video (ajusta según tu estructura)
VIDEO_PATH = "../fase2_computer_vision/data/videos/football_test.mp4"

# Cargar primer frame del video
cap = cv2.VideoCapture(VIDEO_PATH)
ret, frame = cap.read()
cap.release()

if not ret:
    print("❌ No se pudo cargar el video")
    exit()

print("=" * 60)
print("🎯 CALIBRACIÓN DE CANCHA")
print("=" * 60)

# Mostrar frame y dimensiones
height, width = frame.shape[:2]
print(f"\n📹 Video cargado: {width}x{height} pixeles")

# Guardar frame para referencia
cv2.imwrite('src/data/outputs/calibration_frame.jpg', frame)
print(f"✅ Frame guardado en: outputs/calibration_frame.jpg")

print("""
📋 INSTRUCCIONES:

1. Abre la imagen 'src/data/outputs/calibration_frame.jpg'

2. Identifica 4 puntos de referencia que puedas reconocer.
   Ejemplos de puntos fáciles de identificar:
   - Esquinas del área grande
   - Esquinas del área chica  
   - Punto penal
   - Centro de la cancha
   - Esquinas de la cancha

3. Anota las coordenadas en pixeles de esos 4 puntos
   (puedes usar Paint, Photoshop, o cualquier editor de imagen)

4. Determina las coordenadas reales en metros de esos puntos
   
📐 DIMENSIONES DE REFERENCIA (cancha estándar 105x68m):
   - Área grande: 16.5m de profundidad, 40.3m de ancho
   - Área chica: 5.5m de profundidad, 18.3m de ancho
   - Punto penal: 11m desde línea de gol
   - Círculo central: radio 9.15m
""")

# Por ahora, vamos a usar valores aproximados basados en tu video
# Después puedes ajustarlos con la herramienta interactiva

print("\n" + "=" * 60)
print("🔧 CONFIGURACIÓN MANUAL")
print("=" * 60)

print("""
Voy a mostrarte el frame. Necesito que me digas:
- ¿Puedes ver las líneas de la cancha claramente?
- ¿Qué partes de la cancha son visibles? (área, centro, etc.)

Por ahora usaremos una aproximación basada en el tamaño del frame.
""")

# Aproximación simple: asumir que el frame cubre cierta porción de la cancha
# Esto es una estimación inicial que puedes refinar después

# Crear transformación aproximada (asumiendo vista de media cancha)
transformer = PitchTransformer()

# Puntos aproximados (esquinas del frame -> porción de cancha visible)
# Ajusta estos valores según lo que se ve en tu video
pixel_points = [
    (0, 0),              # Esquina superior izquierda del frame
    (width, 0),          # Esquina superior derecha
    (0, height),         # Esquina inferior izquierda
    (width, height)      # Esquina inferior derecha
]

# Asumimos que el video muestra aproximadamente media cancha
# Ajusta estos valores según tu video
pitch_points = [
    (20, 10),            # Corresponde a esquina superior izq del frame
    (85, 10),            # Corresponde a esquina superior der
    (20, 58),            # Corresponde a esquina inferior izq
    (85, 58)             # Corresponde a esquina inferior der
]

transformer.set_transform_from_points(pixel_points, pitch_points)

# Guardar configuración
config = {
    'pixel_points': pixel_points,
    'pitch_points': pitch_points,
    'video_width': width,
    'video_height': height
}

with open('src/data/pitch_calibration.json', 'w') as f:
    json.dump(config, f, indent=2)

print(f"\n✅ Configuración guardada en: data/pitch_calibration.json")

# Probar con un punto central
test_pixel = (width // 2, height // 2)
test_pitch = transformer.pixel_to_pitch(test_pixel[0], test_pixel[1])

print(f"\n📍 Prueba de conversión:")
print(f"   Centro del frame: {test_pixel} pixeles")
print(f"   En cancha: ({test_pitch[0]:.1f}m, {test_pitch[1]:.1f}m)")

print(f"""
⚠️  NOTA: Esta es una aproximación inicial.
    Para mayor precisión, ajusta los valores en 'data/pitch_calibration.json'
    basándote en puntos de referencia reales que veas en tu video.
""")