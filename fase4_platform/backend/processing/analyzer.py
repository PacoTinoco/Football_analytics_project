"""
Módulo de análisis de video de fútbol.
Integra YOLO, tracking y métricas.
"""

from ultralytics import YOLO
import supervision as sv
import cv2
import numpy as np
import pandas as pd
import os


def analyze_football_video(video_path: str, job_id: str, progress_callback=None):
    """
    Analiza un video de fútbol completo.
    
    Args:
        video_path: Ruta al video
        job_id: ID del trabajo
        progress_callback: Función para reportar progreso
    
    Returns:
        dict con resultados del análisis
    """
    
    # Cargar modelo
    model = YOLO('yolov8n.pt')
    tracker = sv.ByteTrack()
    
    # Abrir video
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Almacenar detecciones
    all_detections = []
    
    frame_num = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detectar
        results = model(frame, verbose=False, conf=0.3, classes=[0, 32])[0]
        detections = sv.Detections.from_ultralytics(results)
        
        # Tracking
        detections = tracker.update_with_detections(detections)
        
        # Guardar detecciones
        for i in range(len(detections)):
            x1, y1, x2, y2 = detections.xyxy[i]
            tracker_id = detections.tracker_id[i] if detections.tracker_id is not None else i
            
            all_detections.append({
                'frame': frame_num,
                'time_sec': float(frame_num / fps),
                'tracker_id': int(tracker_id),
                'class': model.names[detections.class_id[i]],
                'center_x': float((x1 + x2) / 2),
                'center_y': float((y1 + y2) / 2)
            })
        
        frame_num += 1
        
        # Reportar progreso
        if progress_callback and frame_num % 30 == 0:
            progress = int(100 * frame_num / total_frames)
            progress_callback(progress)
    
    cap.release()
    
    # Crear DataFrame
    df = pd.DataFrame(all_detections)
    
    # Calcular métricas
    players = df[df['class'] == 'person']
    ball = df[df['class'] == 'sports ball']
    
    # Métricas por jugador
    player_metrics = []
    for tracker_id in players['tracker_id'].unique():
        player_data = players[players['tracker_id'] == tracker_id].sort_values('frame')
        
        if len(player_data) < 2:
            continue
        
        # Calcular distancia
        dx = player_data['center_x'].diff()
        dy = player_data['center_y'].diff()
        distances = np.sqrt(dx**2 + dy**2)
        total_distance = float(distances.sum())
        
        player_metrics.append({
            'tracker_id': int(tracker_id),
            'frames_tracked': int(len(player_data)),
            'total_distance_px': round(total_distance, 2)
        })
    
    # Ordenar por distancia
    player_metrics = sorted(player_metrics, key=lambda x: x['total_distance_px'], reverse=True)
    
    # Resultados - asegurar que todos los valores son tipos nativos de Python
    results = {
        'video_info': {
            'filename': os.path.basename(video_path),
            'duration_sec': round(float(total_frames / fps), 2),
            'fps': round(float(fps), 2),
            'resolution': f"{int(width)}x{int(height)}",
            'total_frames': int(total_frames)
        },
        'detection_summary': {
            'total_detections': int(len(df)),
            'player_detections': int(len(players)),
            'ball_detections': int(len(ball)),
            'unique_players_tracked': int(players['tracker_id'].nunique())
        },
        'player_metrics': player_metrics[:15],  # Top 15
        'analysis_complete': True
    }
    
    return results