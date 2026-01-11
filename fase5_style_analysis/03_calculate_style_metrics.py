"""
Calcular métricas de estilo de juego para Argentina y Francia.
"""

import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)

print("=" * 60)
print("📊 ANÁLISIS DE ESTILO DE JUEGO")
print("=" * 60)

# Cargar datos
argentina = pd.read_pickle('data/argentina_events.pkl')
france = pd.read_pickle('data/france_events.pkl')

def calculate_style_metrics(events, team_name):
    """
    Calcula métricas completas de estilo de juego.
    """
    metrics = {'team': team_name}
    
    # === POSESIÓN Y PASES ===
    passes = events[events['type'] == 'Pass'].copy()
    completed_passes = passes[passes['pass_outcome'].isna()]
    
    metrics['total_passes'] = len(passes)
    metrics['pass_accuracy'] = round(len(completed_passes) / len(passes) * 100, 1)
    
    # Longitud de pases
    if 'pass_length' in passes.columns:
        metrics['avg_pass_length'] = round(passes['pass_length'].mean(), 1)
        metrics['long_passes_pct'] = round((passes['pass_length'] > 30).sum() / len(passes) * 100, 1)
        metrics['short_passes_pct'] = round((passes['pass_length'] < 15).sum() / len(passes) * 100, 1)
    
    # Pases progresivos (avanzan hacia portería rival)
    if 'location' in passes.columns and 'pass_end_location' in passes.columns:
        def is_progressive(row):
            try:
                start_x = row['location'][0] if isinstance(row['location'], list) else 0
                end_x = row['pass_end_location'][0] if isinstance(row['pass_end_location'], list) else 0
                return end_x > start_x + 10  # Avanza más de 10 metros
            except:
                return False
        
        passes['is_progressive'] = passes.apply(is_progressive, axis=1)
        metrics['progressive_passes_pct'] = round(passes['is_progressive'].sum() / len(passes) * 100, 1)
    
    # Pases al área
    if 'pass_end_location' in passes.columns:
        def is_to_box(row):
            try:
                end_x = row['pass_end_location'][0] if isinstance(row['pass_end_location'], list) else 0
                end_y = row['pass_end_location'][1] if isinstance(row['pass_end_location'], list) else 0
                return end_x > 102 and 18 < end_y < 62  # Área rival
            except:
                return False
        
        passes['is_to_box'] = passes.apply(is_to_box, axis=1)
        metrics['passes_to_box'] = passes['is_to_box'].sum()
        metrics['passes_to_box_per_game'] = round(passes['is_to_box'].sum() / events['match_id'].nunique(), 1)
    
    # === ZONAS DE JUEGO ===
    if 'location' in events.columns:
        def get_zone(location):
            try:
                x = location[0] if isinstance(location, list) else 0
                if x < 40:
                    return 'defensive'
                elif x < 80:
                    return 'middle'
                else:
                    return 'attacking'
            except:
                return 'unknown'
        
        events_with_loc = events[events['location'].notna()].copy()
        events_with_loc['zone'] = events_with_loc['location'].apply(get_zone)
        
        zone_counts = events_with_loc['zone'].value_counts(normalize=True) * 100
        metrics['pct_defensive_third'] = round(zone_counts.get('defensive', 0), 1)
        metrics['pct_middle_third'] = round(zone_counts.get('middle', 0), 1)
        metrics['pct_attacking_third'] = round(zone_counts.get('attacking', 0), 1)
    
    # === ATAQUE ===
    shots = events[events['type'] == 'Shot']
    goals = shots[shots['shot_outcome'] == 'Goal']
    
    metrics['total_shots'] = len(shots)
    metrics['goals'] = len(goals)
    metrics['shots_per_game'] = round(len(shots) / events['match_id'].nunique(), 1)
    metrics['conversion_rate'] = round(len(goals) / len(shots) * 100, 1) if len(shots) > 0 else 0
    
    # xG si está disponible
    if 'shot_statsbomb_xg' in shots.columns:
        metrics['total_xg'] = round(shots['shot_statsbomb_xg'].sum(), 2)
        metrics['xg_per_game'] = round(metrics['total_xg'] / events['match_id'].nunique(), 2)
        metrics['xg_overperformance'] = round(len(goals) - metrics['total_xg'], 2)
    
    # === PRESSING Y RECUPERACIÓN ===
    pressures = events[events['type'] == 'Pressure']
    metrics['total_pressures'] = len(pressures)
    metrics['pressures_per_game'] = round(len(pressures) / events['match_id'].nunique(), 1)
    
    # Recuperaciones
    recoveries = events[events['type'] == 'Ball Recovery']
    metrics['ball_recoveries'] = len(recoveries)
    
    # Recuperaciones en zona alta
    if 'location' in recoveries.columns and len(recoveries) > 0:
        def is_high_recovery(row):
            try:
                x = row['location'][0] if isinstance(row['location'], list) else 0
                return x > 60
            except:
                return False
        
        recoveries_copy = recoveries.copy()
        recoveries_copy['is_high'] = recoveries_copy.apply(is_high_recovery, axis=1)
        metrics['high_recoveries_pct'] = round(recoveries_copy['is_high'].sum() / len(recoveries) * 100, 1)
    
    # === DUELOS Y REGATES ===
    dribbles = events[events['type'] == 'Dribble']
    successful_dribbles = dribbles[dribbles['dribble_outcome'] == 'Complete']
    metrics['dribbles_attempted'] = len(dribbles)
    metrics['dribble_success_rate'] = round(len(successful_dribbles) / len(dribbles) * 100, 1) if len(dribbles) > 0 else 0
    
    # === JUEGO DIRECTO VS POSESIÓN ===
    carries = events[events['type'] == 'Carry']
    metrics['total_carries'] = len(carries)
    
    # Ratio pases/carries indica estilo (más pases = más posesión)
    metrics['pass_to_carry_ratio'] = round(len(passes) / len(carries), 2) if len(carries) > 0 else 0
    
    # === LATERALIDAD ===
    if 'location' in passes.columns:
        def get_side(location):
            try:
                y = location[1] if isinstance(location, list) else 40
                if y < 27:
                    return 'left'
                elif y > 53:
                    return 'right'
                else:
                    return 'center'
            except:
                return 'center'
        
        passes['side'] = passes['location'].apply(get_side)
        side_counts = passes['side'].value_counts(normalize=True) * 100
        metrics['pct_left_side'] = round(side_counts.get('left', 0), 1)
        metrics['pct_center'] = round(side_counts.get('center', 0), 1)
        metrics['pct_right_side'] = round(side_counts.get('right', 0), 1)
    
    # === MÉTRICAS POR PARTIDO ===
    num_games = events['match_id'].nunique()
    metrics['games_played'] = num_games
    metrics['goals_per_game'] = round(len(goals) / num_games, 2)
    metrics['passes_per_game'] = round(len(passes) / num_games, 1)
    
    return metrics


# Calcular métricas para ambos equipos
print("\n⏳ Calculando métricas de Argentina...")
argentina_metrics = calculate_style_metrics(argentina, 'Argentina')

print("⏳ Calculando métricas de Francia...")
france_metrics = calculate_style_metrics(france, 'France')

# Crear DataFrame comparativo
comparison = pd.DataFrame([argentina_metrics, france_metrics])
comparison = comparison.set_index('team').T

# Mostrar comparación
print("\n" + "=" * 60)
print("📊 COMPARACIÓN DE ESTILOS DE JUEGO")
print("=" * 60)

print("\n🔄 POSESIÓN Y PASES:")
print("-" * 40)
poss_metrics = ['total_passes', 'pass_accuracy', 'avg_pass_length', 
                'long_passes_pct', 'short_passes_pct', 'progressive_passes_pct',
                'passes_to_box_per_game']
for metric in poss_metrics:
    if metric in comparison.index:
        arg_val = comparison.loc[metric, 'Argentina']
        fra_val = comparison.loc[metric, 'France']
        winner = '🇦🇷' if arg_val > fra_val else '🇫🇷' if fra_val > arg_val else '='
        print(f"   {metric:30} | {arg_val:>8} | {fra_val:>8} | {winner}")

print("\n⚽ ATAQUE:")
print("-" * 40)
attack_metrics = ['total_shots', 'goals', 'shots_per_game', 'conversion_rate',
                  'total_xg', 'xg_per_game', 'xg_overperformance']
for metric in attack_metrics:
    if metric in comparison.index:
        arg_val = comparison.loc[metric, 'Argentina']
        fra_val = comparison.loc[metric, 'France']
        winner = '🇦🇷' if arg_val > fra_val else '🇫🇷' if fra_val > arg_val else '='
        print(f"   {metric:30} | {arg_val:>8} | {fra_val:>8} | {winner}")

print("\n🏃 PRESSING Y RECUPERACIÓN:")
print("-" * 40)
press_metrics = ['pressures_per_game', 'ball_recoveries', 'high_recoveries_pct']
for metric in press_metrics:
    if metric in comparison.index:
        arg_val = comparison.loc[metric, 'Argentina']
        fra_val = comparison.loc[metric, 'France']
        winner = '🇦🇷' if arg_val > fra_val else '🇫🇷' if fra_val > arg_val else '='
        print(f"   {metric:30} | {arg_val:>8} | {fra_val:>8} | {winner}")

print("\n🎯 REGATES Y DUELOS:")
print("-" * 40)
duel_metrics = ['dribbles_attempted', 'dribble_success_rate']
for metric in duel_metrics:
    if metric in comparison.index:
        arg_val = comparison.loc[metric, 'Argentina']
        fra_val = comparison.loc[metric, 'France']
        winner = '🇦🇷' if arg_val > fra_val else '🇫🇷' if fra_val > arg_val else '='
        print(f"   {metric:30} | {arg_val:>8} | {fra_val:>8} | {winner}")

print("\n📍 ZONAS DE JUEGO:")
print("-" * 40)
zone_metrics = ['pct_defensive_third', 'pct_middle_third', 'pct_attacking_third',
                'pct_left_side', 'pct_center', 'pct_right_side']
for metric in zone_metrics:
    if metric in comparison.index:
        arg_val = comparison.loc[metric, 'Argentina']
        fra_val = comparison.loc[metric, 'France']
        print(f"   {metric:30} | {arg_val:>8} | {fra_val:>8}")

# Guardar métricas
comparison.to_csv('data/style_comparison.csv')
print(f"\n✅ Comparación guardada en: data/style_comparison.csv")

# Interpretación automática del estilo
print("\n" + "=" * 60)
print("🎯 INTERPRETACIÓN DEL ESTILO DE JUEGO")
print("=" * 60)

for team, metrics in [('Argentina', argentina_metrics), ('France', france_metrics)]:
    print(f"\n{'🇦🇷' if team == 'Argentina' else '🇫🇷'} {team.upper()}:")
    
    # Determinar estilo de posesión
    if metrics['pass_accuracy'] > 84:
        poss_style = "Alta precisión de pase"
    else:
        poss_style = "Juego más directo"
    
    # Determinar verticalidad
    if metrics.get('progressive_passes_pct', 0) > 15:
        vert_style = "Muy vertical"
    elif metrics.get('progressive_passes_pct', 0) > 10:
        vert_style = "Moderadamente vertical"
    else:
        vert_style = "Paciente en construcción"
    
    # Determinar pressing
    if metrics.get('pressures_per_game', 0) > 150:
        press_style = "Pressing alto intenso"
    elif metrics.get('pressures_per_game', 0) > 100:
        press_style = "Pressing moderado"
    else:
        press_style = "Bloque bajo"
    
    # Determinar eficiencia
    if metrics.get('conversion_rate', 0) > 20:
        eff_style = "Muy eficiente en ataque"
    else:
        eff_style = "Eficiencia normal"
    
    print(f"   • {poss_style}")
    print(f"   • {vert_style}")
    print(f"   • {press_style}")
    print(f"   • {eff_style}")
    print(f"   • Goles sobre xG: {metrics.get('xg_overperformance', 'N/A')}")