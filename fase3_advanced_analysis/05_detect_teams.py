"""
Detecta equipos por color - Versión mejorada.
Toma región central del jugador para evitar el césped.
"""

from ultralytics import YOLO
import cv2
import numpy as np
import pandas as pd

model = YOLO('../fase2_computer_vision/models/yolov8n.pt')
video_path = "../fase2_computer_vision/data/videos/football_test.mp4"


def get_shirt_color(image, bbox):
    """
    Extrae el color de la camiseta tomando solo el centro del bounding box.
    """
    x1, y1, x2, y2 = map(int, bbox)
    
    # Calcular región central (evitar bordes con césped)
    width = x2 - x1
    height = y2 - y1
    
    # Tomar solo el centro: 30% central horizontalmente, 20-50% verticalmente (torso)
    margin_x = int(width * 0.35)
    top_y = y1 + int(height * 0.15)
    bottom_y = y1 + int(height * 0.45)
    
    center_x1 = x1 + margin_x
    center_x2 = x2 - margin_x
    
    # Verificar que la región sea válida
    if center_x2 <= center_x1 or bottom_y <= top_y:
        return None
    
    # Recortar región del torso
    roi = image[top_y:bottom_y, center_x1:center_x2]
    
    if roi.size == 0 or roi.shape[0] < 5 or roi.shape[1] < 5:
        return None
    
    # Convertir a HSV
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # Calcular promedios
    avg_hue = np.mean(hsv[:, :, 0])
    avg_saturation = np.mean(hsv[:, :, 1])
    avg_brightness = np.mean(hsv[:, :, 2])
    
    return {
        'hue': avg_hue,
        'saturation': avg_saturation,
        'brightness': avg_brightness
    }


def classify_team_v2(color_info):
    """
    Clasifica equipo con umbrales ajustados - v3.
    """
    if color_info is None:
        return 'unknown'
    
    hue = color_info['hue']
    brightness = color_info['brightness']
    saturation = color_info['saturation']
    
    # Real Madrid: Blanco (alto brillo, baja saturación)
    if brightness > 160 and saturation < 70:
        return 'real_madrid'
    
    # Barcelona: Azulgrana
    # Rojo/Granate: hue 0-20 o 160-180
    if (hue <= 20 or hue >= 160) and saturation > 100:
        return 'barcelona'
    
    # Azul oscuro del Barcelona: hue 100-140
    if 100 <= hue <= 140 and saturation > 80:
        return 'barcelona'
    
    # Árbitro: Muy oscuro
    if brightness < 60:
        return 'referee'
    
    # Real Madrid alternativo: muy brillante aunque tenga algo de color
    if brightness > 180:
        return 'real_madrid'
    
    # Barcelona: saturación muy alta con brillo medio-bajo
    if saturation > 140 and brightness < 130 and 40 <= hue <= 80:
        return 'barcelona'
    
    return 'unknown'


# Procesar video
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)

print("🎨 Detectando equipos (versión mejorada)...")

team_detections = []
frame_num = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    if frame_num % 10 == 0:
        results = model(frame, verbose=False, conf=0.3, classes=[0])[0]
        
        for box in results.boxes:
            bbox = box.xyxy[0].tolist()
            color_info = get_shirt_color(frame, bbox)
            team = classify_team_v2(color_info)
            
            if team != 'grass':  # Excluir detecciones de césped
                center_x = (bbox[0] + bbox[2]) / 2
                center_y = (bbox[1] + bbox[3]) / 2
                
                team_detections.append({
                    'frame': frame_num,
                    'time_sec': frame_num / fps,
                    'center_x': center_x,
                    'center_y': center_y,
                    'team': team,
                    'brightness': color_info['brightness'] if color_info else 0,
                    'saturation': color_info['saturation'] if color_info else 0,
                    'hue': color_info['hue'] if color_info else 0
                })
    
    frame_num += 1
    if frame_num % 100 == 0:
        print(f"   Procesados: {frame_num} frames")

cap.release()

# Crear DataFrame
df = pd.DataFrame(team_detections)
df.to_csv('src/data/team_detections_v2.csv', index=False)

print(f"\n✅ Datos guardados: data/team_detections_v2.csv")

# Estadísticas
print(f"\n📊 Distribución de equipos:")
team_counts = df['team'].value_counts()
total = len(df)
for team, count in team_counts.items():
    print(f"   {team}: {count} ({100*count/total:.1f}%)")

# Colores promedio por equipo
print(f"\n🎨 Colores promedio por equipo:")
for team in ['real_madrid', 'barcelona', 'referee', 'unknown']:
    subset = df[df['team'] == team]
    if len(subset) > 0:
        print(f"   {team}:")
        print(f"      Brillo: {subset['brightness'].mean():.1f}")
        print(f"      Saturación: {subset['saturation'].mean():.1f}")
        print(f"      Hue: {subset['hue'].mean():.1f}")