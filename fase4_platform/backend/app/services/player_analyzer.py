"""
Servicio de análisis de jugadores.
"""

from statsbombpy import sb
import pandas as pd
import numpy as np


def get_player_events(player_name: str) -> pd.DataFrame:
    """Obtiene eventos de un jugador del Mundial 2022."""
    
    matches = sb.matches(competition_id=43, season_id=106)
    
    all_events = []
    for _, match in matches.iterrows():
        events = sb.events(match_id=match['match_id'])
        player_events = events[events['player'].str.contains(player_name, na=False)]
        if len(player_events) > 0:
            all_events.append(player_events)
    
    if not all_events:
        return pd.DataFrame()
    
    return pd.concat(all_events, ignore_index=True)


def analyze_single_player(player_name: str) -> dict:
    """Analiza métricas de un jugador."""
    
    events = get_player_events(player_name)
    
    if len(events) == 0:
        return {"error": f"No se encontraron datos para {player_name}"}
    
    # Goles
    shots = events[events['type'] == 'Shot']
    goals = shots[shots['shot_outcome'] == 'Goal']
    xg = shots['shot_statsbomb_xg'].sum() if 'shot_statsbomb_xg' in shots.columns else 0
    
    # Asistencias
    passes = events[events['type'] == 'Pass']
    assists = passes[passes['pass_goal_assist'] == True]
    key_passes = passes[passes['pass_shot_assist'] == True]
    completed_passes = passes[passes['pass_outcome'].isna()]
    
    # Regates
    dribbles = events[events['type'] == 'Dribble']
    successful_dribbles = dribbles[dribbles['dribble_outcome'] == 'Complete']
    
    return {
        'player': player_name,
        'matches': events['match_id'].nunique(),
        'total_actions': int(len(events)),
        'goals': int(len(goals)),
        'assists': int(len(assists)),
        'xg': round(float(xg), 2),
        'goals_over_xg': round(len(goals) - xg, 2),
        'shots': int(len(shots)),
        'key_passes': int(len(key_passes)),
        'passes': int(len(passes)),
        'pass_accuracy': round(len(completed_passes) / len(passes) * 100, 1) if len(passes) > 0 else 0,
        'dribbles_attempted': int(len(dribbles)),
        'dribbles_successful': int(len(successful_dribbles)),
        'dribble_success_rate': round(len(successful_dribbles) / len(dribbles) * 100, 1) if len(dribbles) > 0 else 0
    }


def compare_two_players(player1: str, player2: str) -> dict:
    """Compara dos jugadores."""
    
    stats1 = analyze_single_player(player1)
    stats2 = analyze_single_player(player2)
    
    if 'error' in stats1 or 'error' in stats2:
        return {"error": "No se pudieron obtener datos de uno o ambos jugadores"}
    
    return {
        'player1': stats1,
        'player2': stats2,
        'comparison': {
            'more_goals': player1 if stats1['goals'] > stats2['goals'] else player2 if stats2['goals'] > stats1['goals'] else 'Empate',
            'more_assists': player1 if stats1['assists'] > stats2['assists'] else player2 if stats2['assists'] > stats1['assists'] else 'Empate',
            'better_conversion': player1 if stats1['goals_over_xg'] > stats2['goals_over_xg'] else player2,
            'more_creative': player1 if stats1['key_passes'] > stats2['key_passes'] else player2,
            'better_dribbler': player1 if stats1['dribble_success_rate'] > stats2['dribble_success_rate'] else player2
        }
    }