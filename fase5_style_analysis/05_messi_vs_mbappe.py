"""
Análisis comparativo: Messi vs Mbappé - Mundial 2022
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from scipy.ndimage import gaussian_filter

pd.set_option('display.max_columns', None)

print("=" * 60)
print("⚽ MESSI vs MBAPPÉ - MUNDIAL 2022")
print("=" * 60)

# Cargar datos
argentina = pd.read_pickle('data/argentina_events.pkl')
france = pd.read_pickle('data/france_events.pkl')

# Filtrar eventos de cada jugador
messi_events = argentina[argentina['player'].str.contains('Messi', na=False)].copy()
mbappe_events = france[france['player'].str.contains('Mbappé', na=False)].copy()

print(f"\n📊 Eventos cargados:")
print(f"   Messi: {len(messi_events):,} eventos")
print(f"   Mbappé: {len(mbappe_events):,} eventos")


def analyze_player(events, player_name):
    """
    Calcula métricas completas para un jugador.
    """
    metrics = {'player': player_name}
    
    # === PARTIDOS JUGADOS ===
    metrics['matches'] = events['match_id'].nunique()
    
    # === GOLES ===
    shots = events[events['type'] == 'Shot']
    goals = shots[shots['shot_outcome'] == 'Goal']
    metrics['goals'] = len(goals)
    metrics['shots'] = len(shots)
    metrics['shots_on_target'] = len(shots[shots['shot_outcome'].isin(['Goal', 'Saved'])])
    metrics['conversion_rate'] = round(len(goals) / len(shots) * 100, 1) if len(shots) > 0 else 0
    
    # xG
    if 'shot_statsbomb_xg' in shots.columns:
        metrics['xg'] = round(shots['shot_statsbomb_xg'].sum(), 2)
        metrics['xg_per_shot'] = round(metrics['xg'] / len(shots), 3) if len(shots) > 0 else 0
        metrics['goals_minus_xg'] = round(len(goals) - metrics['xg'], 2)
    
    # === ASISTENCIAS ===
    passes = events[events['type'] == 'Pass']
    assists = passes[passes['pass_goal_assist'] == True]
    metrics['assists'] = len(assists)
    
    # Pases clave (generaron tiro)
    key_passes = passes[passes['pass_shot_assist'] == True]
    metrics['key_passes'] = len(key_passes)
    
    # === PASES ===
    completed_passes = passes[passes['pass_outcome'].isna()]
    metrics['passes_attempted'] = len(passes)
    metrics['passes_completed'] = len(completed_passes)
    metrics['pass_accuracy'] = round(len(completed_passes) / len(passes) * 100, 1) if len(passes) > 0 else 0
    
    # Pases progresivos
    def is_progressive(row):
        try:
            start_x = row['location'][0] if isinstance(row['location'], list) else 0
            end_x = row['pass_end_location'][0] if isinstance(row['pass_end_location'], list) else 0
            return end_x > start_x + 10
        except:
            return False
    
    passes_copy = passes.copy()
    passes_copy['is_progressive'] = passes_copy.apply(is_progressive, axis=1)
    metrics['progressive_passes'] = passes_copy['is_progressive'].sum()
    
    # Pases al área
    def is_to_box(row):
        try:
            end_x = row['pass_end_location'][0] if isinstance(row['pass_end_location'], list) else 0
            end_y = row['pass_end_location'][1] if isinstance(row['pass_end_location'], list) else 0
            return end_x > 102 and 18 < end_y < 62
        except:
            return False
    
    passes_copy['is_to_box'] = passes_copy.apply(is_to_box, axis=1)
    metrics['passes_to_box'] = passes_copy['is_to_box'].sum()
    
    # === REGATES ===
    dribbles = events[events['type'] == 'Dribble']
    successful_dribbles = dribbles[dribbles['dribble_outcome'] == 'Complete']
    metrics['dribbles_attempted'] = len(dribbles)
    metrics['dribbles_successful'] = len(successful_dribbles)
    metrics['dribble_success_rate'] = round(len(successful_dribbles) / len(dribbles) * 100, 1) if len(dribbles) > 0 else 0
    
    # === CARRIES (conducciones) ===
    carries = events[events['type'] == 'Carry']
    metrics['carries'] = len(carries)
    
    # Distancia conducida
    def carry_distance(row):
        try:
            start = row['location']
            end = row['carry_end_location']
            if isinstance(start, list) and isinstance(end, list):
                return np.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
        except:
            pass
        return 0
    
    carries_copy = carries.copy()
    carries_copy['distance'] = carries_copy.apply(carry_distance, axis=1)
    metrics['total_carry_distance'] = round(carries_copy['distance'].sum(), 1)
    
    # === ACCIONES DEFENSIVAS ===
    metrics['ball_recoveries'] = len(events[events['type'] == 'Ball Recovery'])
    metrics['pressures'] = len(events[events['type'] == 'Pressure'])
    
    # === FALTAS ===
    metrics['fouls_won'] = len(events[events['type'] == 'Foul Won'])
    metrics['fouls_committed'] = len(events[events['type'] == 'Foul Committed'])
    
    # === PARTICIPACIÓN ===
    metrics['total_actions'] = len(events)
    metrics['actions_per_match'] = round(len(events) / metrics['matches'], 1)
    
    # === ZONA PROMEDIO ===
    events_with_loc = events[events['location'].notna()]
    if len(events_with_loc) > 0:
        avg_x = events_with_loc['location'].apply(lambda x: x[0] if isinstance(x, list) else 0).mean()
        avg_y = events_with_loc['location'].apply(lambda x: x[1] if isinstance(x, list) else 0).mean()
        metrics['avg_position_x'] = round(avg_x, 1)
        metrics['avg_position_y'] = round(avg_y, 1)
    
    return metrics


# Calcular métricas para ambos jugadores
print("\n⏳ Analizando a Messi...")
messi_metrics = analyze_player(messi_events, "Lionel Messi")

print("⏳ Analizando a Mbappé...")
mbappe_metrics = analyze_player(mbappe_events, "Kylian Mbappé")

# Crear DataFrame comparativo
comparison = pd.DataFrame([messi_metrics, mbappe_metrics])
comparison = comparison.set_index('player').T

# Mostrar comparación
print("\n" + "=" * 60)
print("📊 COMPARACIÓN COMPLETA")
print("=" * 60)

categories = {
    'PARTICIPACIÓN': ['matches', 'total_actions', 'actions_per_match'],
    'GOLES': ['goals', 'shots', 'shots_on_target', 'conversion_rate', 'xg', 'goals_minus_xg'],
    'CREATIVIDAD': ['assists', 'key_passes', 'passes_to_box', 'progressive_passes'],
    'PASES': ['passes_attempted', 'passes_completed', 'pass_accuracy'],
    'REGATES': ['dribbles_attempted', 'dribbles_successful', 'dribble_success_rate'],
    'CONDUCCIÓN': ['carries', 'total_carry_distance'],
    'OTROS': ['fouls_won', 'ball_recoveries', 'avg_position_x', 'avg_position_y']
}

for category, metrics_list in categories.items():
    print(f"\n{category}:")
    print("-" * 50)
    for metric in metrics_list:
        if metric in comparison.index:
            messi_val = comparison.loc[metric, 'Lionel Messi']
            mbappe_val = comparison.loc[metric, 'Kylian Mbappé']
            
            # Determinar ganador
            if isinstance(messi_val, (int, float)) and isinstance(mbappe_val, (int, float)):
                if metric in ['fouls_committed']:  # Menos es mejor
                    winner = '🇦🇷' if messi_val < mbappe_val else '🇫🇷' if mbappe_val < messi_val else '='
                else:
                    winner = '🇦🇷' if messi_val > mbappe_val else '🇫🇷' if mbappe_val > messi_val else '='
            else:
                winner = ''
            
            print(f"   {metric:25} | {str(messi_val):>10} | {str(mbappe_val):>10} | {winner}")

# Guardar comparación
comparison.to_csv('data/messi_vs_mbappe.csv')
print(f"\n✅ Comparación guardada en: data/messi_vs_mbappe.csv")


# ============================================================
# VISUALIZACIONES
# ============================================================

print("\n⏳ Generando visualizaciones...")

def draw_pitch(ax):
    """Dibuja una cancha de fútbol."""
    # Configuración
    pitch_length = 120
    pitch_width = 80
    
    # Color de fondo
    ax.set_facecolor('#2e8b2e')
    
    # Líneas
    lw = 2
    lc = 'white'
    
    # Contorno
    ax.plot([0, pitch_length], [0, 0], color=lc, lw=lw)
    ax.plot([0, pitch_length], [pitch_width, pitch_width], color=lc, lw=lw)
    ax.plot([0, 0], [0, pitch_width], color=lc, lw=lw)
    ax.plot([pitch_length, pitch_length], [0, pitch_width], color=lc, lw=lw)
    
    # Línea media
    ax.plot([pitch_length/2, pitch_length/2], [0, pitch_width], color=lc, lw=lw)
    
    # Círculo central
    circle = plt.Circle((pitch_length/2, pitch_width/2), 9.15, fill=False, color=lc, lw=lw)
    ax.add_patch(circle)
    
    # Áreas
    # Izquierda
    ax.plot([0, 16.5], [pitch_width/2 - 20.15, pitch_width/2 - 20.15], color=lc, lw=lw)
    ax.plot([0, 16.5], [pitch_width/2 + 20.15, pitch_width/2 + 20.15], color=lc, lw=lw)
    ax.plot([16.5, 16.5], [pitch_width/2 - 20.15, pitch_width/2 + 20.15], color=lc, lw=lw)
    
    # Derecha
    ax.plot([pitch_length, pitch_length - 16.5], [pitch_width/2 - 20.15, pitch_width/2 - 20.15], color=lc, lw=lw)
    ax.plot([pitch_length, pitch_length - 16.5], [pitch_width/2 + 20.15, pitch_width/2 + 20.15], color=lc, lw=lw)
    ax.plot([pitch_length - 16.5, pitch_length - 16.5], [pitch_width/2 - 20.15, pitch_width/2 + 20.15], color=lc, lw=lw)
    
    ax.set_xlim(-5, pitch_length + 5)
    ax.set_ylim(-5, pitch_width + 5)
    ax.set_aspect('equal')
    ax.axis('off')


def create_heatmap(events, ax, title, color):
    """Crea mapa de calor de las acciones de un jugador."""
    draw_pitch(ax)
    
    # Extraer coordenadas
    coords = events[events['location'].notna()]['location'].apply(
        lambda x: x if isinstance(x, list) else [0, 0]
    ).tolist()
    
    if len(coords) > 0:
        x_coords = [c[0] for c in coords]
        y_coords = [c[1] for c in coords]
        
        # Crear heatmap
        heatmap, xedges, yedges = np.histogram2d(x_coords, y_coords, bins=25, 
                                                   range=[[0, 120], [0, 80]])
        heatmap = gaussian_filter(heatmap, sigma=2)
        
        # Mostrar
        extent = [0, 120, 0, 80]
        ax.imshow(heatmap.T, extent=extent, origin='lower', cmap=color, alpha=0.6)
        
        # Punto promedio
        avg_x = np.mean(x_coords)
        avg_y = np.mean(y_coords)
        ax.scatter(avg_x, avg_y, s=200, c='white', edgecolors='black', 
                  linewidth=2, zorder=10, marker='*')
    
    ax.set_title(title, fontsize=14, fontweight='bold', color='white')


# Crear figura con múltiples visualizaciones
fig = plt.figure(figsize=(18, 14))

# 1. Mapas de calor
ax1 = fig.add_subplot(2, 3, 1)
create_heatmap(messi_events, ax1, 'Messi - Mapa de Calor', 'YlOrRd')

ax2 = fig.add_subplot(2, 3, 2)
create_heatmap(mbappe_events, ax2, 'Mbappé - Mapa de Calor', 'Blues')

# 3. Radar comparativo
ax3 = fig.add_subplot(2, 3, 3, polar=True)

categories_radar = ['Goles', 'Asistencias', 'Pases Clave', 'Regates\nExitosos', 
                    'Precisión\nPase', 'xG']

# Normalizar valores (0-100)
messi_radar = [
    messi_metrics['goals'] / 9 * 100,  # Max 9 goles
    messi_metrics['assists'] / 5 * 100,  # Max 5 asistencias
    messi_metrics['key_passes'] / 20 * 100,  # Max 20
    messi_metrics['dribbles_successful'] / 20 * 100,  # Max 20
    messi_metrics['pass_accuracy'],
    messi_metrics['xg'] / 10 * 100  # Max 10 xG
]

mbappe_radar = [
    mbappe_metrics['goals'] / 9 * 100,
    mbappe_metrics['assists'] / 5 * 100,
    mbappe_metrics['key_passes'] / 20 * 100,
    mbappe_metrics['dribbles_successful'] / 20 * 100,
    mbappe_metrics['pass_accuracy'],
    mbappe_metrics['xg'] / 10 * 100
]

# Ángulos
angles = np.linspace(0, 2 * np.pi, len(categories_radar), endpoint=False).tolist()
angles += angles[:1]
messi_radar += messi_radar[:1]
mbappe_radar += mbappe_radar[:1]

ax3.plot(angles, messi_radar, 'o-', linewidth=2, label='Messi', color='#75AADB')
ax3.fill(angles, messi_radar, alpha=0.25, color='#75AADB')
ax3.plot(angles, mbappe_radar, 'o-', linewidth=2, label='Mbappé', color='#002654')
ax3.fill(angles, mbappe_radar, alpha=0.25, color='#002654')

ax3.set_xticks(angles[:-1])
ax3.set_xticklabels(categories_radar, size=9)
ax3.set_ylim(0, 100)
ax3.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
ax3.set_title('Comparación de Habilidades', fontsize=12, fontweight='bold')

# 4. Goles por partido
ax4 = fig.add_subplot(2, 3, 4)
metrics_bar = ['Goles', 'Asistencias', 'Pases Clave', 'Regates\nExitosos']
messi_vals = [messi_metrics['goals'], messi_metrics['assists'], 
              messi_metrics['key_passes'], messi_metrics['dribbles_successful']]
mbappe_vals = [mbappe_metrics['goals'], mbappe_metrics['assists'],
               mbappe_metrics['key_passes'], mbappe_metrics['dribbles_successful']]

x = np.arange(len(metrics_bar))
width = 0.35

bars1 = ax4.bar(x - width/2, messi_vals, width, label='Messi', color='#75AADB')
bars2 = ax4.bar(x + width/2, mbappe_vals, width, label='Mbappé', color='#002654')

ax4.set_ylabel('Cantidad')
ax4.set_title('Producción Ofensiva', fontweight='bold')
ax4.set_xticks(x)
ax4.set_xticklabels(metrics_bar)
ax4.legend()

# Añadir valores
for bar, val in zip(bars1, messi_vals):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            str(val), ha='center', va='bottom', fontsize=10)
for bar, val in zip(bars2, mbappe_vals):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            str(val), ha='center', va='bottom', fontsize=10)

# 5. Eficiencia (xG vs Goles)
ax5 = fig.add_subplot(2, 3, 5)

ax5.scatter(messi_metrics['xg'], messi_metrics['goals'], s=400, 
           c='#75AADB', edgecolors='black', linewidth=2, label='Messi', zorder=5)
ax5.scatter(mbappe_metrics['xg'], mbappe_metrics['goals'], s=400,
           c='#002654', edgecolors='white', linewidth=2, label='Mbappé', zorder=5)

# Línea de referencia
max_val = max(messi_metrics['xg'], mbappe_metrics['xg'], 
              messi_metrics['goals'], mbappe_metrics['goals']) + 1
ax5.plot([0, max_val], [0, max_val], 'k--', alpha=0.5, label='Rendimiento esperado')

ax5.set_xlabel('Expected Goals (xG)')
ax5.set_ylabel('Goles Reales')
ax5.set_title('Eficiencia Goleadora', fontweight='bold')
ax5.legend()
ax5.grid(True, alpha=0.3)

# Anotaciones
ax5.annotate(f"Messi\n({messi_metrics['xg']} xG, {messi_metrics['goals']} goles)",
            (messi_metrics['xg'], messi_metrics['goals']),
            textcoords="offset points", xytext=(10, 10), fontsize=9)
ax5.annotate(f"Mbappé\n({mbappe_metrics['xg']} xG, {mbappe_metrics['goals']} goles)",
            (mbappe_metrics['xg'], mbappe_metrics['goals']),
            textcoords="offset points", xytext=(10, -20), fontsize=9)

# 6. Resumen de texto
ax6 = fig.add_subplot(2, 3, 6)
ax6.axis('off')

summary_text = f"""
RESUMEN COMPARATIVO
━━━━━━━━━━━━━━━━━━━━

           MESSI          MBAPPÉ
Goles:        {messi_metrics['goals']}              {mbappe_metrics['goals']}
Asistencias:  {messi_metrics['assists']}              {mbappe_metrics['assists']}
G + A:        {messi_metrics['goals'] + messi_metrics['assists']}             {mbappe_metrics['goals'] + mbappe_metrics['assists']}

xG:           {messi_metrics['xg']}           {mbappe_metrics['xg']}
Sobre xG:     +{messi_metrics['goals_minus_xg']}          +{mbappe_metrics['goals_minus_xg']}

Pases Clave:  {messi_metrics['key_passes']}             {mbappe_metrics['key_passes']}
Regates:      {messi_metrics['dribbles_successful']}/{messi_metrics['dribbles_attempted']}          {mbappe_metrics['dribbles_successful']}/{mbappe_metrics['dribbles_attempted']}
% Regates:    {messi_metrics['dribble_success_rate']}%         {mbappe_metrics['dribble_success_rate']}%

━━━━━━━━━━━━━━━━━━━━
CONCLUSIÓN:
Messi: Más completo, mejor creador
Mbappé: Más letal, puro goleador
"""

ax6.text(0.1, 0.95, summary_text, transform=ax6.transAxes,
        fontsize=11, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.suptitle('⚽ MESSI vs MBAPPÉ - Mundial Qatar 2022', 
             fontsize=18, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('outputs/messi_vs_mbappe.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

print("✅ Guardado: outputs/messi_vs_mbappe.png")

print("\n" + "=" * 60)
print("✅ ANÁLISIS COMPLETADO")
print("=" * 60)