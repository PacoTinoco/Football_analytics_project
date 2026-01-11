"""
Cargar todos los eventos de Argentina y Francia en el Mundial 2022.
"""

from statsbombpy import sb
import pandas as pd
import json
from tqdm import tqdm

pd.set_option('display.max_columns', None)

print("=" * 60)
print("📥 CARGANDO DATOS COMPLETOS - ARGENTINA Y FRANCIA")
print("=" * 60)

# Cargar partidos
matches = sb.matches(competition_id=43, season_id=106)

# Filtrar por equipo
argentina_matches = matches[
    (matches['home_team'] == 'Argentina') | 
    (matches['away_team'] == 'Argentina')
]

france_matches = matches[
    (matches['home_team'] == 'France') | 
    (matches['away_team'] == 'France')
]

def load_team_events(team_matches, team_name):
    """Carga todos los eventos de un equipo."""
    all_events = []
    all_frames = []
    
    print(f"\n⏳ Cargando {len(team_matches)} partidos de {team_name}...")
    
    for _, match in tqdm(team_matches.iterrows(), total=len(team_matches)):
        match_id = match['match_id']
        
        # Cargar eventos
        events = sb.events(match_id=match_id)
        events['match_id'] = match_id
        events['match_date'] = match['match_date']
        events['home_team'] = match['home_team']
        events['away_team'] = match['away_team']
        events['home_score'] = match['home_score']
        events['away_score'] = match['away_score']
        
        # Determinar oponente
        if match['home_team'] == team_name:
            events['opponent'] = match['away_team']
            events['is_home'] = True
        else:
            events['opponent'] = match['home_team']
            events['is_home'] = False
        
        all_events.append(events)
        
        # Cargar frames 360
        try:
            frames = sb.frames(match_id=match_id)
            frames['match_id'] = match_id
            all_frames.append(frames)
        except:
            pass
    
    events_df = pd.concat(all_events, ignore_index=True)
    
    if all_frames:
        frames_df = pd.concat(all_frames, ignore_index=True)
    else:
        frames_df = pd.DataFrame()
    
    return events_df, frames_df

# Cargar Argentina
argentina_events, argentina_frames = load_team_events(argentina_matches, 'Argentina')
argentina_only = argentina_events[argentina_events['team'] == 'Argentina'].copy()

# Cargar Francia
france_events, france_frames = load_team_events(france_matches, 'France')
france_only = france_events[france_events['team'] == 'France'].copy()

# Resumen
print("\n" + "=" * 60)
print("📊 RESUMEN DE DATOS CARGADOS")
print("=" * 60)

print(f"\n🇦🇷 ARGENTINA:")
print(f"   Eventos totales: {len(argentina_only):,}")
print(f"   Partidos: {argentina_only['match_id'].nunique()}")
print(f"   Jugadores únicos: {argentina_only['player'].nunique()}")

print(f"\n🇫🇷 FRANCIA:")
print(f"   Eventos totales: {len(france_only):,}")
print(f"   Partidos: {france_only['match_id'].nunique()}")
print(f"   Jugadores únicos: {france_only['player'].nunique()}")

# Jugadores más activos
print(f"\n👥 Top 10 jugadores Argentina (por acciones):")
print(argentina_only['player'].value_counts().head(10).to_string())

print(f"\n👥 Top 10 jugadores Francia (por acciones):")
print(france_only['player'].value_counts().head(10).to_string())

# Guardar datos
argentina_only.to_pickle('data/argentina_events.pkl')
france_only.to_pickle('data/france_events.pkl')
argentina_events.to_pickle('data/argentina_all_events.pkl')
france_events.to_pickle('data/france_all_events.pkl')

print(f"\n✅ Datos guardados:")
print(f"   - data/argentina_events.pkl")
print(f"   - data/france_events.pkl")

# Estadísticas básicas
print("\n" + "=" * 60)
print("⚽ ESTADÍSTICAS BÁSICAS DEL TORNEO")
print("=" * 60)

for team_name, team_events in [('Argentina', argentina_only), ('France', france_only)]:
    print(f"\n{'🇦🇷' if team_name == 'Argentina' else '🇫🇷'} {team_name.upper()}:")
    
    # Goles
    shots = team_events[team_events['type'] == 'Shot']
    goals = shots[shots['shot_outcome'] == 'Goal']
    print(f"   Goles: {len(goals)}")
    
    # Goleadores
    if len(goals) > 0:
        print(f"   Goleadores: {goals['player'].value_counts().head(5).to_dict()}")
    
    # Pases
    passes = team_events[team_events['type'] == 'Pass']
    completed = passes[passes['pass_outcome'].isna()]
    accuracy = len(completed) / len(passes) * 100 if len(passes) > 0 else 0
    print(f"   Pases: {len(passes):,} ({accuracy:.1f}% precisión)")
    
    # Tiros
    print(f"   Tiros: {len(shots)} ({len(goals)} goles)")