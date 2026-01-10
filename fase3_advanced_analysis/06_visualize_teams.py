"""
Visualiza la posición de cada equipo en la cancha.
"""

import pandas as pd
import matplotlib.pyplot as plt
import json
import sys
sys.path.append('src')
from pitch_transform import PitchTransformer

# Cargar calibración
with open('src/data/pitch_calibration.json', 'r') as f:
    config = json.load(f)

transformer = PitchTransformer()
transformer.set_transform_from_points(config['pixel_points'], config['pitch_points'])

# Cargar datos de equipos
df = pd.read_csv('src/data/team_detections_v2.csv')

# Transformar a coordenadas de cancha
df = transformer.transform_dataframe(df, x_col='center_x', y_col='center_y')

# Filtrar puntos válidos
df = df[(df['pitch_x'] >= 0) & (df['pitch_x'] <= 105) &
        (df['pitch_y'] >= 0) & (df['pitch_y'] <= 68)]

print(f"📊 Datos cargados: {len(df)} detecciones válidas")


def draw_pitch(ax):
    """Dibuja cancha de fútbol."""
    ax.set_facecolor('#2e8b2e')
    lw, lc = 2, 'white'
    
    # Contorno
    ax.plot([0, 105], [0, 0], color=lc, lw=lw)
    ax.plot([0, 105], [68, 68], color=lc, lw=lw)
    ax.plot([0, 0], [0, 68], color=lc, lw=lw)
    ax.plot([105, 105], [0, 68], color=lc, lw=lw)
    
    # Línea central y círculo
    ax.plot([52.5, 52.5], [0, 68], color=lc, lw=lw)
    circle = plt.Circle((52.5, 34), 9.15, fill=False, color=lc, lw=lw)
    ax.add_patch(circle)
    
    # Áreas
    ax.plot([0, 16.5, 16.5, 0], [13.85, 13.85, 54.15, 54.15], color=lc, lw=lw)
    ax.plot([105, 88.5, 88.5, 105], [13.85, 13.85, 54.15, 54.15], color=lc, lw=lw)
    
    ax.set_xlim(-2, 107)
    ax.set_ylim(-2, 70)
    ax.set_aspect('equal')
    ax.axis('off')


# Crear figura
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Colores por equipo
colors = {
    'real_madrid': 'white',
    'barcelona': '#a50044',  # Granate
    'referee': 'yellow',
    'unknown': 'gray'
}

# 1. Todas las detecciones por equipo
ax1 = axes[0, 0]
draw_pitch(ax1)
for team, color in colors.items():
    team_data = df[df['team'] == team]
    ax1.scatter(team_data['pitch_x'], team_data['pitch_y'],
                c=color, s=20, alpha=0.5, label=f'{team} ({len(team_data)})',
                edgecolors='black', linewidth=0.3)
ax1.legend(loc='upper left', fontsize=8)
ax1.set_title('Todas las Detecciones por Equipo', fontweight='bold', color='white')

# 2. Solo Real Madrid
ax2 = axes[0, 1]
draw_pitch(ax2)
rm = df[df['team'] == 'real_madrid']
ax2.scatter(rm['pitch_x'], rm['pitch_y'], c='white', s=40, 
            edgecolors='black', linewidth=0.5, alpha=0.6)
ax2.set_title(f'Real Madrid ({len(rm)} detecciones)', fontweight='bold', color='white')

# 3. Solo Barcelona
ax3 = axes[1, 0]
draw_pitch(ax3)
barca = df[df['team'] == 'barcelona']
ax3.scatter(barca['pitch_x'], barca['pitch_y'], c='#a50044', s=40,
            edgecolors='gold', linewidth=0.5, alpha=0.6)
ax3.set_title(f'Barcelona ({len(barca)} detecciones)', fontweight='bold', color='white')

# 4. Comparación de posición promedio
ax4 = axes[1, 1]
draw_pitch(ax4)

for team, color in [('real_madrid', 'white'), ('barcelona', '#a50044')]:
    team_data = df[df['team'] == team]
    if len(team_data) > 0:
        avg_x = team_data['pitch_x'].mean()
        avg_y = team_data['pitch_y'].mean()
        ax4.scatter(avg_x, avg_y, c=color, s=500, edgecolors='black', 
                   linewidth=3, zorder=10, label=f'{team}')
        ax4.annotate(f'{team}\n({avg_x:.1f}, {avg_y:.1f})', 
                    (avg_x, avg_y + 5), ha='center', fontsize=9, color='white')

ax4.legend(loc='upper left')
ax4.set_title('Posición Promedio por Equipo', fontweight='bold', color='white')

plt.tight_layout()
plt.savefig('src/data/outputs/team_positions.png', dpi=150, bbox_inches='tight', facecolor='#1a1a1a')
plt.show()

print(f"\n✅ Gráfico guardado: outputs/team_positions.png")