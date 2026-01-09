import pandas as pd
import matplotlib.pyplot as plt

# Cargar datos
df = pd.read_csv('detections.csv')

print(f"📊 Datos cargados: {len(df)} detecciones")

# Filtrar solo personas (jugadores)
players = df[df['class'] == 'person']
ball = df[df['class'] == 'sports ball']

# Crear visualización
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 1. Mapa de calor de posiciones de jugadores
ax1 = axes[0]
ax1.scatter(players['center_x'], players['center_y'], 
            alpha=0.3, s=10, c='blue', label='Jugadores')
ax1.scatter(ball['center_x'], ball['center_y'], 
            alpha=0.5, s=30, c='red', label='Balón')
ax1.set_xlabel('Posición X (pixeles)')
ax1.set_ylabel('Posición Y (pixeles)')
ax1.set_title('Mapa de Posiciones Detectadas')
ax1.legend()
ax1.invert_yaxis()  # Invertir Y para que coincida con el video

# 2. Jugadores detectados por frame
ax2 = axes[1]
players_per_frame = players.groupby('frame').size()
ax2.plot(players_per_frame.index, players_per_frame.values, color='green')
ax2.set_xlabel('Frame')
ax2.set_ylabel('Jugadores detectados')
ax2.set_title('Jugadores Detectados por Frame')
ax2.axhline(y=players_per_frame.mean(), color='red', linestyle='--', 
            label=f'Promedio: {players_per_frame.mean():.1f}')
ax2.legend()

plt.tight_layout()
plt.savefig('positions_analysis.png', dpi=150)
plt.show()

print(f"\n✅ Gráfico guardado: positions_analysis.png")
print(f"\n📈 Estadísticas:")
print(f"   Promedio jugadores por frame: {players_per_frame.mean():.1f}")
print(f"   Máximo detectados: {players_per_frame.max()}")
print(f"   Mínimo detectados: {players_per_frame.min()}")