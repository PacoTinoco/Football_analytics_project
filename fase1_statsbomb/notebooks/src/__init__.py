"""
Football Analytics Project
===========================

Módulos para análisis de fútbol con Machine Learning.

Principales componentes:
- oart: Cálculo de Opportunity-Adjusted Risk Taking
- visualization: Funciones de visualización
- data_loader: Carga de datos StatsBomb

Uso básico:
    from src.oart import OARTCalculator
    from src.visualization import create_pass_map
"""

from .oart import (
    OARTCalculator,
    FeatureExtractor,
    calculate_split_half_reliability,
    load_statsbomb_passes,
    load_statsbomb_frames
)

__version__ = "0.1.0"
__author__ = "Tu Nombre"

__all__ = [
    'OARTCalculator',
    'FeatureExtractor', 
    'calculate_split_half_reliability',
    'load_statsbomb_passes',
    'load_statsbomb_frames'
]
