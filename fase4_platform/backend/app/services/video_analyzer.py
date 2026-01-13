"""
Servicio de análisis de video con YOLO.
"""

from ultralytics import YOLO
import supervision as sv
import cv2
import numpy as np
import os


def analyze_video_full(video_path: str, job_id: str) -> dict:
    """
    Analiza un video completo con YOLO y tracking.
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
    
    # Procesar frames
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
        
        # Guardar
        for i in range(len(detections)):
            x1, y1, x2, y2 = detections.xyxy[i]
            tracker_id = int(detections.tracker_id[i]) if detections.tracker_id is not None else i
            
            all_detections.append({
                'frame': frame_num,
                'tracker_id': tracker_id,
                'class': model.names[detections.class_id[i]],
                'center_x': float((x1 + x2) / 2),
                'center_y': float((y1 + y2) / 2)
            })
        
        frame_num += 1
    
    cap.release()
    
    # Calcular métricas
    players = [d for d in all_detections if d['class'] == 'person']
    balls = [d for d in all_detections if d['class'] == 'sports ball']
    
    # Métricas por jugador
    player_ids = set(d['tracker_id'] for d in players)
    player_metrics = []
    
    for pid in player_ids:
        p_detections = sorted([d for d in players if d['tracker_id'] == pid], 
                             key=lambda x: x['frame'])
        
        if len(p_detections) < 2:
            continue
        
        # Distancia total
        total_dist = 0
        for i in range(1, len(p_detections)):
            dx = p_detections[i]['center_x'] - p_detections[i-1]['center_x']
            dy = p_detections[i]['center_y'] - p_detections[i-1]['center_y']
            total_dist += np.sqrt(dx**2 + dy**2)
        
        player_metrics.append({
            'tracker_id': pid,
            'frames_tracked': len(p_detections),
            'distance_px': round(total_dist, 2)
        })
    
    player_metrics = sorted(player_metrics, key=lambda x: x['distance_px'], reverse=True)
    
    return {
        'video_info': {
            'duration_sec': round(total_frames / fps, 2),
            'fps': round(fps, 2),
            'resolution': f"{width}x{height}",
            'total_frames': total_frames
        },
        'detection_summary': {
            'total_detections': len(all_detections),
            'player_detections': len(players),
            'ball_detections': len(balls),
            'unique_players': len(player_ids)
        },
        'player_metrics': player_metrics[:15]
    }