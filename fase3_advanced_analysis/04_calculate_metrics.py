"""
Calcula métricas físicas: distancia recorrida, velocidad, sprints.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Cargar datos
df = pd.read_csv('src/data/tracking_pitch_coords.csv')
players = df[df['class'] == 'person'].copy()

# Obtener FPS del video (asumimos 30 FPS, ajusta si es diferente)
FPS = 30
TIME_BETWEEN_FRAMES = 1 / FPS

print("📊 Calculando métricas físicas...")
print(f"   FPS asumido: {FPS}")

# Calcular distancia y velocidad para cada jugador
metrics = []

for tracker_id in players['tracker_id'].unique():
    player_data = players[players['tracker_id'] == tracker_id].sort_values('frame')
    
    if len(player_data) < 2:
        continue
    
    # Calcular distancia entre frames consecutivos
    player_data = player_data.copy()
    player_data['dx'] = player_data['pitch_x'].diff()
    player_data['dy'] = player_data['pitch_y'].diff()
    player_data['distance'] = np.sqrt(player_data['dx']**2 + player_data['dy']**2)
    
    # Calcular diferencia de frames (para manejar frames no consecutivos)
    player_data['frame_diff'] = player_data['frame'].diff()
    
    # Velocidad (metros por segundo)
    player_data['velocity'] = player_data['distance'] / (player_data['frame_diff'] / FPS)
    
    # Filtrar velocidades irreales (> 12 m/s = 43 km/h es imposible)
    player_data.loc[player_data['velocity'] > 12, 'velocity'] = np.nan
    player_data.loc[player_data['distance'] > 5, 'distance'] = np.nan  # Saltos muy grandes = error
    
    # Calcular métricas agregadas
    total_distance = player_data['distance'].sum()
    avg_velocity = player_data['velocity'].mean()
    max_velocity = player_data['velocity'].max()
    num_frames = len(player_data)
    
    # Contar sprints (velocidad > 7 m/s = 25 km/h)
    sprints = (player_data['velocity'] > 7).sum()
    
    metrics.append({
        'tracker_id': tracker_id,
        'frames_tracked': num_frames,
        'time_tracked_sec': num_frames / FPS,
        'total_distance_m': round(total_distance, 2),
        'avg_velocity_ms': round(avg_velocity, 2) if not np.isnan(avg_velocity) else 0,
        'max_velocity_ms': round(max_velocity, 2) if not np.isnan(max_velocity) else 0,
        'max_velocity_kmh': round(max_velocity * 3.6, 1) if not np.isnan(max_velocity) else 0,
        'sprints': sprints
    })

# Crear DataFrame de métricas
metrics_df = pd.DataFrame(metrics)
metrics_df = metrics_df.sort_values('total_distance_m', ascending=False)

# Filtrar jugadores con suficiente tiempo de tracking (más de 2 segundos)
metrics_df = metrics_df[metrics_df['time_tracked_sec'] > 2]

print(f"\n✅ Métricas calculadas para {len(metrics_df)} jugadores")

# Guardar métricas
metrics_df.to_csv('src/data/player_metrics.csv', index=False)
print(f"✅ Guardado: src/data/player_metrics.csv")

# Mostrar top 10
print(f"\n🏃 TOP 10 - Mayor distancia recorrida:")
print("-" * 80)
print(metrics_df.head(10).to_string(index=False))

# Estadísticas generales
print(f"\n📈 Estadísticas generales:")
print(f"   Distancia promedio: {metrics_df['total_distance_m'].mean():.1f} m")
print(f"   Velocidad máxima registrada: {metrics_df['max_velocity_kmh'].max():.1f} km/h")
print(f"   Total de sprints detectados: {metrics_df['sprints'].sum()}")

# Crear visualización
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# 1. Distancia recorrida (top 15)
ax1 = axes[0, 0]
top15 = metrics_df.head(15)
ax1.barh(range(len(top15)), top15['total_distance_m'], color='#3498db')
ax1.set_yticks(range(len(top15)))
ax1.set_yticklabels([f"#{int(id)}" for id in top15['tracker_id']])
ax1.set_xlabel('Distancia (metros)')
ax1.set_title('Top 15 - Distancia Recorrida', fontweight='bold')
ax1.invert_yaxis()

# 2. Velocidad máxima (top 15)
ax2 = axes[0, 1]
top15_vel = metrics_df.nlargest(15, 'max_velocity_kmh')
ax2.barh(range(len(top15_vel)), top15_vel['max_velocity_kmh'], color='#e74c3c')
ax2.set_yticks(range(len(top15_vel)))
ax2.set_yticklabels([f"#{int(id)}" for id in top15_vel['tracker_id']])
ax2.set_xlabel('Velocidad (km/h)')
ax2.set_title('Top 15 - Velocidad Máxima', fontweight='bold')
ax2.invert_yaxis()

# 3. Distribución de velocidades
ax3 = axes[1, 0]
all_velocities = players.copy()
all_velocities['velocity'] = np.nan
# Recalcular para el histograma
for tracker_id in players['tracker_id'].unique():
    mask = players['tracker_id'] == tracker_id
    player_data = players[mask].sort_values('frame')
    if len(player_data) > 1:
        dx = player_data['pitch_x'].diff()
        dy = player_data['pitch_y'].diff()
        dist = np.sqrt(dx**2 + dy**2)
        frame_diff = player_data['frame'].diff()
        vel = dist / (frame_diff / FPS)
        vel[vel > 12] = np.nan
        all_velocities.loc[mask, 'velocity'] = vel.values

velocities_clean = all_velocities['velocity'].dropna()
velocities_clean = velocities_clean[velocities_clean < 12]
ax3.hist(velocities_clean, bins=30, color='#2ecc71', edgecolor='black', alpha=0.7)
ax3.axvline(x=7, color='red', linestyle='--', label='Sprint (>7 m/s)')
ax3.set_xlabel('Velocidad (m/s)')
ax3.set_ylabel('Frecuencia')
ax3.set_title('Distribución de Velocidades', fontweight='bold')
ax3.legend()

# 4. Tiempo tracked vs Distancia
ax4 = axes[1, 1]
ax4.scatter(metrics_df['time_tracked_sec'], metrics_df['total_distance_m'], 
            alpha=0.6, c='#9b59b6', s=50)
ax4.set_xlabel('Tiempo trackeado (segundos)')
ax4.set_ylabel('Distancia recorrida (metros)')
ax4.set_title('Tiempo vs Distancia', fontweight='bold')

plt.tight_layout()
plt.savefig('src/data/outputs/player_metrics.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\n✅ Gráfico guardado: outputs/player_metrics.png")