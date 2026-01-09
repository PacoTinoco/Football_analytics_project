"""
Transforma los datos de tracking de pixeles a coordenadas de cancha.
"""

import pandas as pd
import json
import sys
sys.path.append('src')
from pitch_transform import PitchTransformer

# Cargar configuración de calibración
with open('src/data/pitch_calibration.json', 'r') as f:
    config = json.load(f)

print("📐 Configuración de calibración cargada")
print(f"   Video: {config['video_width']}x{config['video_height']} px")

# Crear transformador
transformer = PitchTransformer()
transformer.set_transform_from_points(
    config['pixel_points'],
    config['pitch_points']
)

# Cargar datos de tracking de la Fase 2
tracking_path = "../fase2_computer_vision/data/videos/outputs/tracking_data.csv"
df = pd.read_csv(tracking_path)

print(f"\n📊 Datos de tracking cargados: {len(df)} detecciones")

# Transformar coordenadas
print("🔄 Transformando coordenadas...")
df = transformer.transform_dataframe(df, x_col='center_x', y_col='center_y')

# Filtrar puntos que caen fuera de la cancha (errores)
df_valid = df[
    (df['pitch_x'] >= 0) & (df['pitch_x'] <= 105) &
    (df['pitch_y'] >= 0) & (df['pitch_y'] <= 68)
].copy()

print(f"   Puntos válidos: {len(df_valid)} de {len(df)} ({100*len(df_valid)/len(df):.1f}%)")

# Guardar datos transformados
output_path = "src/data/tracking_pitch_coords.csv"
df_valid.to_csv(output_path, index=False)
print(f"\n✅ Datos guardados: {output_path}")

# Mostrar resumen
print(f"\n📋 Muestra de datos transformados:")
print(df_valid[['frame', 'tracker_id', 'class', 'center_x', 'center_y', 'pitch_x', 'pitch_y']].head(10).to_string(index=False))

# Estadísticas
print(f"\n📈 Estadísticas de posiciones (en metros):")
players = df_valid[df_valid['class'] == 'person']
print(f"   Rango X: {players['pitch_x'].min():.1f}m - {players['pitch_x'].max():.1f}m")
print(f"   Rango Y: {players['pitch_y'].min():.1f}m - {players['pitch_y'].max():.1f}m")