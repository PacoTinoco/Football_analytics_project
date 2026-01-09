import pandas as pd
import matplotlib.pyplot as plt

# Cargar datos
df = pd.read_csv('tracking_data.csv')

# Filtrar solo personas
players = df[df['class'] == 'person']

# Encontrar los jugadores con más detecciones (los más "estables")
top_players = players['tracker_id'].value_counts().head(8).index.tolist()

print(f"📊 Jugadores con más detecciones (IDs): {top_players}")

# Crear visualización
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 1. Trayectorias de los jugadores más detectados
ax1 = axes[0]
colors = plt.cm.tab10(range(len(top_players)))

for i, player_id in enumerate(top_players):
    player_data = players[players['tracker_id'] == player_id]
    ax1.plot(player_data['center_x'], player_data['center_y'], 
             '-', alpha=0.7, linewidth=2, color=colors[i],
             label=f'Jugador #{player_id}')
    # Marcar inicio
    ax1.scatter(player_data['center_x'].iloc[0], player_data['center_y'].iloc[0],
                s=100, color=colors[i], marker='o', edgecolors='black', zorder=5)

ax1.set_xlabel('Posición X (pixeles)')
ax1.set_ylabel('Posición Y (pixeles)')
ax1.set_title('Trayectorias de Jugadores')
ax1.legend(loc='upper right', fontsize=8)
ax1.invert_yaxis()

# 2. Movimiento en X a lo largo del tiempo para un jugador
ax2 = axes[1]
main_player = top_players[0]
player_data = players[players['tracker_id'] == main_player]

ax2.plot(player_data['time_sec'], player_data['center_x'], 'b-', label='Posición X')
ax2.plot(player_data['time_sec'], player_data['center_y'], 'r-', label='Posición Y')
ax2.set_xlabel('Tiempo (segundos)')
ax2.set_ylabel('Posición (pixeles)')
ax2.set_title(f'Movimiento del Jugador #{main_player} en el Tiempo')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('trajectories.png', dpi=150)
plt.show()

print(f"\n✅ Gráfico guardado: trajectories.png")