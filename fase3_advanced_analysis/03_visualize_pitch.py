"""
Visualiza las posiciones de tracking sobre una cancha de fútbol.
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Rectangle, Circle
import numpy as np

def draw_pitch(ax, pitch_length=105, pitch_width=68):
    """Dibuja una cancha de fútbol."""
    
    # Color del césped
    ax.set_facecolor('#2e8b2e')
    
    # Líneas blancas
    line_color = 'white'
    lw = 2
    
    # Contorno de la cancha
    ax.plot([0, pitch_length], [0, 0], color=line_color, lw=lw)
    ax.plot([0, pitch_length], [pitch_width, pitch_width], color=line_color, lw=lw)
    ax.plot([0, 0], [0, pitch_width], color=line_color, lw=lw)
    ax.plot([pitch_length, pitch_length], [0, pitch_width], color=line_color, lw=lw)
    
    # Línea central
    ax.plot([pitch_length/2, pitch_length/2], [0, pitch_width], color=line_color, lw=lw)
    
    # Círculo central
    center_circle = Circle((pitch_length/2, pitch_width/2), 9.15, 
                           fill=False, color=line_color, lw=lw)
    ax.add_patch(center_circle)
    
    # Punto central
    ax.scatter(pitch_length/2, pitch_width/2, color=line_color, s=20, zorder=5)
    
    # Área grande izquierda
    ax.plot([0, 16.5], [pitch_width/2 - 20.15, pitch_width/2 - 20.15], color=line_color, lw=lw)
    ax.plot([0, 16.5], [pitch_width/2 + 20.15, pitch_width/2 + 20.15], color=line_color, lw=lw)
    ax.plot([16.5, 16.5], [pitch_width/2 - 20.15, pitch_width/2 + 20.15], color=line_color, lw=lw)
    
    # Área grande derecha
    ax.plot([pitch_length, pitch_length - 16.5], [pitch_width/2 - 20.15, pitch_width/2 - 20.15], color=line_color, lw=lw)
    ax.plot([pitch_length, pitch_length - 16.5], [pitch_width/2 + 20.15, pitch_width/2 + 20.15], color=line_color, lw=lw)
    ax.plot([pitch_length - 16.5, pitch_length - 16.5], [pitch_width/2 - 20.15, pitch_width/2 + 20.15], color=line_color, lw=lw)
    
    # Área chica izquierda
    ax.plot([0, 5.5], [pitch_width/2 - 9.15, pitch_width/2 - 9.15], color=line_color, lw=lw)
    ax.plot([0, 5.5], [pitch_width/2 + 9.15, pitch_width/2 + 9.15], color=line_color, lw=lw)
    ax.plot([5.5, 5.5], [pitch_width/2 - 9.15, pitch_width/2 + 9.15], color=line_color, lw=lw)
    
    # Área chica derecha
    ax.plot([pitch_length, pitch_length - 5.5], [pitch_width/2 - 9.15, pitch_width/2 - 9.15], color=line_color, lw=lw)
    ax.plot([pitch_length, pitch_length - 5.5], [pitch_width/2 + 9.15, pitch_width/2 + 9.15], color=line_color, lw=lw)
    ax.plot([pitch_length - 5.5, pitch_length - 5.5], [pitch_width/2 - 9.15, pitch_width/2 + 9.15], color=line_color, lw=lw)
    
    # Puntos penales
    ax.scatter(11, pitch_width/2, color=line_color, s=20, zorder=5)
    ax.scatter(pitch_length - 11, pitch_width/2, color=line_color, s=20, zorder=5)
    
    # Configurar ejes
    ax.set_xlim(-2, pitch_length + 2)
    ax.set_ylim(-2, pitch_width + 2)
    ax.set_aspect('equal')
    ax.axis('off')
    
    return ax


# Cargar datos transformados
df = pd.read_csv('src/data/tracking_pitch_coords.csv')
players = df[df['class'] == 'person']
ball = df[df['class'] == 'sports ball']

print(f"📊 Datos cargados: {len(players)} posiciones de jugadores")

# Crear figura con 2 gráficos
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 1. Todas las posiciones de jugadores
ax1 = axes[0]
draw_pitch(ax1)
ax1.scatter(players['pitch_x'], players['pitch_y'], 
            alpha=0.3, s=15, c='yellow', edgecolors='black', linewidth=0.5)
ax1.scatter(ball['pitch_x'], ball['pitch_y'], 
            alpha=0.5, s=30, c='white', edgecolors='black', linewidth=1)
ax1.set_title('Todas las Posiciones Detectadas', fontsize=14, fontweight='bold', color='white')

# 2. Posiciones en un frame específico (frame 0)
ax2 = axes[1]
draw_pitch(ax2)

frame_0_players = players[players['frame'] == 0]
frame_0_ball = ball[ball['frame'] == 0]

ax2.scatter(frame_0_players['pitch_x'], frame_0_players['pitch_y'], 
            s=200, c='yellow', edgecolors='black', linewidth=2, zorder=10)
ax2.scatter(frame_0_ball['pitch_x'], frame_0_ball['pitch_y'], 
            s=100, c='white', edgecolors='red', linewidth=2, zorder=10)

# Añadir números de tracker_id
for _, row in frame_0_players.iterrows():
    ax2.annotate(f"{int(row['tracker_id'])}", 
                 (row['pitch_x'], row['pitch_y']),
                 ha='center', va='center', fontsize=8, fontweight='bold')

ax2.set_title('Posiciones en Frame 0 (con IDs)', fontsize=14, fontweight='bold', color='white')

plt.tight_layout()
plt.savefig('src/data/outputs/pitch_positions.png', dpi=150, bbox_inches='tight', facecolor='#1a1a1a')
plt.show()

print(f"\n✅ Gráfico guardado: src/data/outputs/pitch_positions.png")