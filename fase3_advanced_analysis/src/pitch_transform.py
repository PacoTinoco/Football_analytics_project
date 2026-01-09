"""
Módulo para transformar coordenadas de pixeles a coordenadas de cancha real.
Usa homografía para mapear puntos del video a metros.
"""

import numpy as np
import cv2

# Dimensiones oficiales de cancha (en metros)
PITCH_LENGTH = 105.0  # metros
PITCH_WIDTH = 68.0    # metros

class PitchTransformer:
    """
    Transforma coordenadas de pixeles a coordenadas de cancha.
    """
    
    def __init__(self):
        self.matrix = None  # Matriz de homografía
        self.inverse_matrix = None
        
    def set_transform_from_points(self, pixel_points, pitch_points):
        """
        Calcula la matriz de transformación a partir de puntos correspondientes.
        
        Args:
            pixel_points: Lista de 4 puntos en pixeles [(x1,y1), (x2,y2), ...]
            pitch_points: Lista de 4 puntos en metros [(x1,y1), (x2,y2), ...]
        """
        src = np.float32(pixel_points)
        dst = np.float32(pitch_points)
        
        self.matrix = cv2.getPerspectiveTransform(src, dst)
        self.inverse_matrix = cv2.getPerspectiveTransform(dst, src)
        
        print("✅ Matriz de transformación calculada")
        
    def pixel_to_pitch(self, x, y):
        """
        Convierte coordenadas de pixel a coordenadas de cancha.
        
        Args:
            x, y: Coordenadas en pixeles
            
        Returns:
            (pitch_x, pitch_y): Coordenadas en metros
        """
        if self.matrix is None:
            raise ValueError("Primero debes configurar la transformación con set_transform_from_points()")
        
        point = np.float32([[[x, y]]])
        transformed = cv2.perspectiveTransform(point, self.matrix)
        
        return transformed[0][0][0], transformed[0][0][1]
    
    def pitch_to_pixel(self, pitch_x, pitch_y):
        """
        Convierte coordenadas de cancha a pixeles (inverso).
        """
        if self.inverse_matrix is None:
            raise ValueError("Primero debes configurar la transformación")
        
        point = np.float32([[[pitch_x, pitch_y]]])
        transformed = cv2.perspectiveTransform(point, self.inverse_matrix)
        
        return transformed[0][0][0], transformed[0][0][1]
    
    def transform_dataframe(self, df, x_col='center_x', y_col='center_y'):
        """
        Transforma todas las coordenadas de un DataFrame.
        
        Args:
            df: DataFrame con columnas de coordenadas
            x_col, y_col: Nombres de las columnas de coordenadas
            
        Returns:
            DataFrame con nuevas columnas pitch_x, pitch_y
        """
        df = df.copy()
        
        pitch_coords = df.apply(
            lambda row: self.pixel_to_pitch(row[x_col], row[y_col]), 
            axis=1
        )
        
        df['pitch_x'] = [coord[0] for coord in pitch_coords]
        df['pitch_y'] = [coord[1] for coord in pitch_coords]
        
        return df


def select_points_from_frame(video_path, frame_number=0):
    """
    Herramienta interactiva para seleccionar puntos de referencia en un frame.
    
    Args:
        video_path: Ruta al video
        frame_number: Número de frame a usar
        
    Returns:
        Lista de puntos seleccionados
    """
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise ValueError(f"No se pudo leer el frame {frame_number}")
    
    points = []
    
    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            print(f"   Punto {len(points)}: ({x}, {y})")
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
            cv2.putText(frame, str(len(points)), (x+10, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Seleccionar Puntos', frame)
    
    print("\n🎯 Instrucciones:")
    print("   - Click en 4 esquinas conocidas de la cancha")
    print("   - Presiona 'q' cuando termines")
    print("   - Presiona 'r' para reiniciar\n")
    
    cv2.imshow('Seleccionar Puntos', frame)
    cv2.setMouseCallback('Seleccionar Puntos', click_event)
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') and len(points) >= 4:
            break
        elif key == ord('r'):
            points = []
            cap = cv2.VideoCapture(video_path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            cap.release()
            cv2.imshow('Seleccionar Puntos', frame)
            print("   Reiniciado - selecciona los puntos de nuevo")
    
    cv2.destroyAllWindows()
    
    return points[:4]  # Solo los primeros 4 puntos


if __name__ == "__main__":
    # Ejemplo de uso
    print("=" * 50)
    print("PITCH TRANSFORMER - Ejemplo de uso")
    print("=" * 50)
    
    # Crear transformador
    transformer = PitchTransformer()
    
    # Ejemplo con puntos ficticios (deberás ajustar a tu video)
    # Estos son las 4 esquinas del área grande en el video
    pixel_points = [
        (100, 150),   # Esquina superior izquierda
        (800, 150),   # Esquina superior derecha
        (100, 450),   # Esquina inferior izquierda
        (800, 450)    # Esquina inferior derecha
    ]
    
    # Coordenadas reales correspondientes (área grande: 16.5m x 40.3m)
    pitch_points = [
        (0, 13.85),      # Esquina superior izquierda del área
        (16.5, 13.85),   # Esquina superior derecha
        (0, 54.15),      # Esquina inferior izquierda
        (16.5, 54.15)    # Esquina inferior derecha
    ]
    
    transformer.set_transform_from_points(pixel_points, pitch_points)
    
    # Probar conversión
    test_x, test_y = 450, 300
    pitch_x, pitch_y = transformer.pixel_to_pitch(test_x, test_y)
    
    print(f"\n📍 Ejemplo de conversión:")
    print(f"   Pixel: ({test_x}, {test_y})")
    print(f"   Cancha: ({pitch_x:.1f}m, {pitch_y:.1f}m)")