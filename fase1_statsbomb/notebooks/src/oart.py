"""
OART - Opportunity-Adjusted Risk Taking
=======================================

Módulo principal para calcular la métrica OART en análisis de fútbol.

Basado en: "Quantifying Opportunity-Adjusted Risk Taking in Football Pass Selection"
por Lucas Carrasquilla Parra (Universidad del Rosario, 2026)

Uso:
    from src.oart import OARTCalculator
    
    calculator = OARTCalculator(model_path='path/to/model.joblib')
    oart_score = calculator.calculate_event_oart(pass_event)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import joblib


class FeatureExtractor:
    """
    Extrae características de eventos de pase para el modelo de predicción.
    """
    
    @staticmethod
    def extract_spatial_features(start_x: float, start_y: float, 
                                  end_x: float, end_y: float) -> Dict[str, float]:
        """Extrae características espaciales de un pase."""
        return {
            'pass_distance': np.sqrt((end_x - start_x)**2 + (end_y - start_y)**2),
            'pass_angle': np.arctan2(end_y - start_y, end_x - start_x),
            'distance_to_goal_start': np.sqrt((120 - start_x)**2 + (40 - start_y)**2),
            'distance_to_goal_end': np.sqrt((120 - end_x)**2 + (40 - end_y)**2),
        }
    
    @staticmethod
    def extract_zone_features(start_x: float, end_x: float) -> Dict[str, int]:
        """Extrae características de zona del campo."""
        return {
            'start_defensive': 1 if start_x <= 40 else 0,
            'start_middle': 1 if 40 < start_x <= 80 else 0,
            'start_attacking': 1 if start_x > 80 else 0,
            'end_defensive': 1 if end_x <= 40 else 0,
            'end_middle': 1 if 40 < end_x <= 80 else 0,
            'end_attacking': 1 if end_x > 80 else 0,
        }
    
    @staticmethod
    def extract_tactical_features(freeze_frame: List[Dict], 
                                   start_x: float, start_y: float,
                                   end_x: float, end_y: float) -> Dict[str, float]:
        """Extrae características tácticas del freeze frame."""
        if not freeze_frame:
            return {
                'log_option_set_size': np.log1p(5),
                'opponents_in_path': 1,
                'nearest_opponent_dist': 10,
                'teammates_ahead': 3
            }
        
        teammates = [p for p in freeze_frame if p.get('teammate', False) and not p.get('actor', False)]
        opponents = [p for p in freeze_frame if not p.get('teammate', True)]
        
        # Option set size
        option_set_size = len(teammates)
        
        # Opponents in pass corridor
        min_x, max_x = min(start_x, end_x), max(start_x, end_x)
        min_y, max_y = min(start_y, end_y) - 5, max(start_y, end_y) + 5
        
        opponents_in_path = sum(
            1 for p in opponents 
            if min_x <= p['location'][0] <= max_x and min_y <= p['location'][1] <= max_y
        )
        
        # Nearest opponent
        if opponents:
            opp_distances = [
                np.sqrt((p['location'][0] - start_x)**2 + (p['location'][1] - start_y)**2)
                for p in opponents
            ]
            nearest_opponent_dist = min(opp_distances)
        else:
            nearest_opponent_dist = 50
        
        # Teammates ahead
        teammates_ahead = sum(1 for p in teammates if p['location'][0] > start_x)
        
        return {
            'log_option_set_size': np.log1p(option_set_size),
            'opponents_in_path': opponents_in_path,
            'nearest_opponent_dist': nearest_opponent_dist,
            'teammates_ahead': teammates_ahead
        }
    
    @staticmethod
    def extract_contextual_features(minute: int, period: int, 
                                     under_pressure: bool, 
                                     play_pattern: str) -> Dict[str, float]:
        """Extrae características contextuales."""
        return {
            'match_minute_normalized': minute / 90,
            'is_second_half': 1 if period == 2 else 0,
            'is_set_piece': 1 if play_pattern in ['From Corner', 'From Free Kick', 
                                                    'From Throw In', 'From Goal Kick'] else 0,
            'is_regular_play': 1 if play_pattern == 'Regular Play' else 0,
            'under_pressure_int': 1 if under_pressure else 0,
        }
    
    @classmethod
    def extract_all_features(cls, passer_location: List[float], 
                              receiver_location: List[float],
                              freeze_frame: List[Dict],
                              minute: int, period: int,
                              under_pressure: bool, 
                              play_pattern: str) -> Dict[str, float]:
        """
        Extrae todas las características para una opción de pase.
        
        Args:
            passer_location: [x, y] del pasador
            receiver_location: [x, y] del receptor
            freeze_frame: Lista de jugadores en el frame
            minute: Minuto del partido
            period: Período (1 o 2)
            under_pressure: Si está bajo presión
            play_pattern: Tipo de jugada
        
        Returns:
            Dict con todas las características
        """
        start_x, start_y = passer_location
        end_x, end_y = receiver_location
        
        features = {}
        features.update(cls.extract_spatial_features(start_x, start_y, end_x, end_y))
        features.update(cls.extract_zone_features(start_x, end_x))
        features.update(cls.extract_tactical_features(freeze_frame, start_x, start_y, end_x, end_y))
        features.update(cls.extract_contextual_features(minute, period, under_pressure, play_pattern))
        
        return features


class OARTCalculator:
    """
    Calculador de Opportunity-Adjusted Risk Taking (OART).
    
    OART mide la preferencia de riesgo en la selección de pases,
    comparando la opción elegida contra todas las alternativas disponibles.
    
    Attributes:
        model: Modelo XGBoost entrenado para predecir éxito de pases
        feature_list: Lista ordenada de características del modelo
    """
    
    # Orden de características para el modelo
    DEFAULT_FEATURE_ORDER = [
        'pass_distance', 'pass_angle', 'distance_to_goal_start', 'distance_to_goal_end',
        'under_pressure_int', 'log_option_set_size', 'opponents_in_path',
        'nearest_opponent_dist', 'teammates_ahead',
        'match_minute_normalized', 'is_second_half', 'is_set_piece', 'is_regular_play',
        'start_defensive', 'start_middle', 'start_attacking',
        'end_defensive', 'end_middle', 'end_attacking'
    ]
    
    def __init__(self, model_path: Optional[str] = None, 
                 model: Optional[object] = None,
                 feature_list: Optional[List[str]] = None):
        """
        Inicializa el calculador de OART.
        
        Args:
            model_path: Ruta al modelo .joblib
            model: Modelo ya cargado (alternativa a model_path)
            feature_list: Lista de features en orden
        """
        if model is not None:
            self.model = model
        elif model_path:
            self.model = joblib.load(model_path)
        else:
            raise ValueError("Debe proporcionar model_path o model")
        
        self.feature_list = feature_list or self.DEFAULT_FEATURE_ORDER
        self.extractor = FeatureExtractor()
    
    def predict_pass_success(self, features: Dict[str, float]) -> float:
        """
        Predice la probabilidad de éxito de un pase.
        
        Args:
            features: Dict con características del pase
        
        Returns:
            Probabilidad de éxito (0-1)
        """
        X = np.array([[features.get(f, 0) for f in self.feature_list]])
        return self.model.predict_proba(X)[0, 1]
    
    def calculate_event_oart(self, pass_event: Dict) -> Dict[str, float]:
        """
        Calcula OART para un evento de pase individual.
        
        Args:
            pass_event: Dict con datos del pase, incluyendo:
                - location: [x, y] del pasador
                - pass_end_location: [x, y] del receptor
                - freeze_frame: Lista de jugadores
                - minute, period, under_pressure, play_pattern
        
        Returns:
            Dict con:
                - oart: Score OART (0-1)
                - option_set_size: Número de opciones
                - chosen_prob: Probabilidad del pase elegido
                - max_prob: Máxima probabilidad disponible
                - mean_prob: Probabilidad media de opciones
                - prob_rank: Ranking de la opción elegida
        """
        freeze_frame = pass_event.get('freeze_frame')
        
        # Validar freeze frame
        if not freeze_frame or not isinstance(freeze_frame, list):
            return self._empty_result()
        
        # Extraer compañeros disponibles
        teammates = [
            p for p in freeze_frame 
            if p.get('teammate', False) and not p.get('actor', False)
        ]
        
        if len(teammates) < 2:
            return self._empty_result(option_set_size=len(teammates))
        
        # Datos del pase
        passer_location = pass_event['location']
        chosen_location = pass_event['pass_end_location']
        minute = pass_event.get('minute', 45)
        period = pass_event.get('period', 1)
        under_pressure = pass_event.get('under_pressure', False)
        play_pattern = pass_event.get('play_pattern', 'Regular Play')
        
        # Calcular probabilidad para cada opción
        option_probs = []
        for teammate in teammates:
            features = self.extractor.extract_all_features(
                passer_location, teammate['location'], freeze_frame,
                minute, period, under_pressure, play_pattern
            )
            prob = self.predict_pass_success(features)
            option_probs.append(prob)
        
        # Probabilidad del receptor elegido
        chosen_features = self.extractor.extract_all_features(
            passer_location, chosen_location, freeze_frame,
            minute, period, under_pressure, play_pattern
        )
        chosen_prob = self.predict_pass_success(chosen_features)
        
        # === CALCULAR OART ===
        alternatives_better = sum(1 for p in option_probs if p > chosen_prob)
        alternatives_tied = sum(1 for p in option_probs if p == chosen_prob)
        n_alternatives = len(option_probs)
        
        oart = (alternatives_better + 0.5 * alternatives_tied) / n_alternatives
        
        # Ranking de la opción elegida
        all_probs = option_probs + [chosen_prob]
        sorted_probs = sorted(all_probs, reverse=True)
        prob_rank = sorted_probs.index(chosen_prob) + 1
        
        return {
            'oart': oart,
            'option_set_size': len(teammates),
            'chosen_prob': chosen_prob,
            'max_prob': max(option_probs),
            'mean_prob': np.mean(option_probs),
            'prob_rank': prob_rank
        }
    
    def calculate_player_oart(self, events: List[Dict], 
                               min_events: int = 25) -> Dict[str, float]:
        """
        Calcula OART agregado para un jugador.
        
        Args:
            events: Lista de eventos de pase del jugador
            min_events: Mínimo de eventos requeridos
        
        Returns:
            Dict con estadísticas agregadas de OART
        """
        oart_scores = []
        
        for event in events:
            result = self.calculate_event_oart(event)
            if not np.isnan(result['oart']):
                oart_scores.append(result['oart'])
        
        if len(oart_scores) < min_events:
            return {
                'oart_mean': np.nan,
                'oart_std': np.nan,
                'n_events': len(oart_scores),
                'valid': False
            }
        
        return {
            'oart_mean': np.mean(oart_scores),
            'oart_std': np.std(oart_scores),
            'n_events': len(oart_scores),
            'valid': True
        }
    
    @staticmethod
    def _empty_result(option_set_size: float = np.nan) -> Dict[str, float]:
        """Retorna resultado vacío cuando OART no puede calcularse."""
        return {
            'oart': np.nan,
            'option_set_size': option_set_size,
            'chosen_prob': np.nan,
            'max_prob': np.nan,
            'mean_prob': np.nan,
            'prob_rank': np.nan
        }


def calculate_split_half_reliability(df: pd.DataFrame, 
                                      oart_column: str = 'oart',
                                      player_column: str = 'player',
                                      min_events: int = 25,
                                      n_iterations: int = 100) -> Tuple[float, float, List[float]]:
    """
    Calcula la fiabilidad split-half de OART.
    
    Args:
        df: DataFrame con OART a nivel de evento
        oart_column: Nombre de columna con OART
        player_column: Nombre de columna con identificador de jugador
        min_events: Mínimo de eventos por jugador
        n_iterations: Iteraciones para bootstrap
    
    Returns:
        Tuple (mean_correlation, std_correlation, list_of_correlations)
    """
    from scipy import stats
    
    correlations = []
    
    for i in range(n_iterations):
        half1_oart = []
        half2_oart = []
        
        for player, group in df.groupby(player_column):
            if len(group) < min_events:
                continue
            
            shuffled = group.sample(frac=1, random_state=i)
            mid = len(shuffled) // 2
            
            half1_oart.append(shuffled.iloc[:mid][oart_column].mean())
            half2_oart.append(shuffled.iloc[mid:][oart_column].mean())
        
        if len(half1_oart) > 10:
            corr, _ = stats.pearsonr(half1_oart, half2_oart)
            correlations.append(corr)
    
    return np.mean(correlations), np.std(correlations), correlations


# Funciones de conveniencia
def load_statsbomb_passes(competition_id: int, season_id: int) -> pd.DataFrame:
    """
    Carga todos los pases de una competición de StatsBomb.
    
    Args:
        competition_id: ID de la competición
        season_id: ID de la temporada
    
    Returns:
        DataFrame con eventos de pase
    """
    from statsbombpy import sb
    from tqdm import tqdm
    
    matches = sb.matches(competition_id=competition_id, season_id=season_id)
    
    all_passes = []
    for match_id in tqdm(matches['match_id'], desc="Cargando pases"):
        events = sb.events(match_id=match_id)
        passes = events[events['type'] == 'Pass'].copy()
        passes['match_id'] = match_id
        all_passes.append(passes)
    
    return pd.concat(all_passes, ignore_index=True)


def load_statsbomb_frames(competition_id: int, season_id: int) -> pd.DataFrame:
    """
    Carga todos los freeze frames de una competición.
    
    Args:
        competition_id: ID de la competición
        season_id: ID de la temporada
    
    Returns:
        DataFrame con freeze frames
    """
    from statsbombpy import sb
    from tqdm import tqdm
    
    matches = sb.matches(competition_id=competition_id, season_id=season_id)
    
    all_frames = []
    for match_id in tqdm(matches['match_id'], desc="Cargando frames"):
        frames = sb.frames(match_id=match_id)
        frames['match_id'] = match_id
        all_frames.append(frames)
    
    return pd.concat(all_frames, ignore_index=True)


if __name__ == "__main__":
    # Ejemplo de uso
    print("OART Module - Opportunity-Adjusted Risk Taking")
    print("=" * 50)
    print("\nUso:")
    print("  from src.oart import OARTCalculator")
    print("  calculator = OARTCalculator(model_path='model.joblib')")
    print("  result = calculator.calculate_event_oart(pass_event)")
    print("\nPara más información, consulta la documentación.")
