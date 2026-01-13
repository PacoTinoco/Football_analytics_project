"""
Servicio de análisis de equipos con StatsBomb.
"""

from statsbombpy import sb
import pandas as pd
import numpy as np


def get_team_events(team_name: str, competition: str = "worldcup_2022") -> pd.DataFrame:
    """Obtiene todos los eventos de un equipo."""
    
    if competition == "worldcup_2022":
        comp_id, season_id = 43, 106
    else:
        comp_id, season_id = 11, 27
    
    matches = sb.matches(competition_id=comp_id, season_id=season_id)
    team_matches = matches[
        (matches['home_team'] == team_name) | 
        (matches['away_team'] == team_name)
    ]
    
    all_events = []
    for _, match in team_matches.iterrows():
        events = sb.events(match_id=match['match_id'])
        events['match_id'] = match['match_id']
        all_events.append(events)
    
    df = pd.concat(all_events, ignore_index=True)
    return df[df['team'] == team_name]


def analyze_team_style(team_name: str, competition: str = "worldcup_2022") -> dict:
    """Analiza el estilo de juego de un equipo."""
    
    events = get_team_events(team_name, competition)
    
    # Pases
    passes = events[events['type'] == 'Pass']
    completed = passes[passes['pass_outcome'].isna()]
    pass_accuracy = round(len(completed) / len(passes) * 100, 1) if len(passes) > 0 else 0
    
    # Goles
    shots = events[events['type'] == 'Shot']
    goals = shots[shots['shot_outcome'] == 'Goal']
    
    # xG
    xg = round(shots['shot_statsbomb_xg'].sum(), 2) if 'shot_statsbomb_xg' in shots.columns else 0
    
    # Pressing
    pressures = events[events['type'] == 'Pressure']
    num_matches = events['match_id'].nunique()
    
    # Regates
    dribbles = events[events['type'] == 'Dribble']
    successful_dribbles = dribbles[dribbles['dribble_outcome'] == 'Complete']
    dribble_rate = round(len(successful_dribbles) / len(dribbles) * 100, 1) if len(dribbles) > 0 else 0
    
    return {
        'team': team_name,
        'matches': num_matches,
        'goals': int(len(goals)),
        'xg': float(xg),
        'goals_over_xg': round(len(goals) - xg, 2),
        'shots': int(len(shots)),
        'conversion_rate': round(len(goals) / len(shots) * 100, 1) if len(shots) > 0 else 0,
        'passes': int(len(passes)),
        'pass_accuracy': float(pass_accuracy),
        'pressures_per_game': round(len(pressures) / num_matches, 1),
        'dribble_success': float(dribble_rate)
    }


def compare_teams_style(team1: str, team2: str, competition: str) -> dict:
    """Compara estilos de dos equipos."""
    
    style1 = analyze_team_style(team1, competition)
    style2 = analyze_team_style(team2, competition)
    
    return {
        'team1': style1,
        'team2': style2,
        'comparison': {
            'more_goals': team1 if style1['goals'] > style2['goals'] else team2,
            'better_passing': team1 if style1['pass_accuracy'] > style2['pass_accuracy'] else team2,
            'more_pressing': team1 if style1['pressures_per_game'] > style2['pressures_per_game'] else team2,
            'more_efficient': team1 if style1['conversion_rate'] > style2['conversion_rate'] else team2
        }
    }