#!/usr/bin/env python3
"""
Quick Start Script - Football Analytics OART
=============================================

Este script verifica la instalación y descarga datos de ejemplo.

Uso:
    python quick_start.py

Requiere:
    pip install -r requirements.txt
"""

import sys
import os

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas."""
    print("🔍 Verificando dependencias...\n")
    
    required = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'sklearn': 'scikit-learn',
        'xgboost': 'xgboost',
        'statsbombpy': 'statsbombpy',
        'mplsoccer': 'mplsoccer',
        'tqdm': 'tqdm'
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Faltan paquetes. Instala con:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    print("\n✅ Todas las dependencias instaladas correctamente\n")
    return True


def create_directories():
    """Crea la estructura de directorios necesaria."""
    print("📁 Creando estructura de directorios...\n")
    
    dirs = [
        'data/raw',
        'data/processed',
        'outputs/figures',
        'outputs/reports'
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"   ✅ {d}/")
    
    print()


def test_statsbomb_connection():
    """Prueba la conexión con StatsBomb Open Data."""
    print("🌐 Probando conexión con StatsBomb...\n")
    
    try:
        from statsbombpy import sb
        
        # Cargar competiciones
        competitions = sb.competitions()
        print(f"   ✅ Competiciones disponibles: {len(competitions)}")
        
        # Buscar Mundial 2022
        wc2022 = competitions[
            (competitions['competition_name'] == 'FIFA World Cup') & 
            (competitions['season_name'] == '2022')
        ]
        
        if len(wc2022) > 0:
            print(f"   ✅ FIFA World Cup 2022 encontrado")
            print(f"      Competition ID: 43, Season ID: 106")
        
        # Cargar partidos de ejemplo
        matches = sb.matches(competition_id=43, season_id=106)
        print(f"   ✅ Partidos del Mundial: {len(matches)}")
        
        # Cargar eventos de un partido
        match_id = matches['match_id'].iloc[0]
        events = sb.events(match_id=match_id)
        print(f"   ✅ Eventos de ejemplo: {len(events)}")
        
        # Verificar datos 360
        frames = sb.frames(match_id=match_id)
        print(f"   ✅ Freeze frames: {len(frames)}")
        
        print("\n✅ Conexión con StatsBomb exitosa\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error conectando con StatsBomb: {e}")
        return False


def load_sample_data():
    """Carga y guarda datos de ejemplo para pruebas rápidas."""
    print("📥 Descargando datos de ejemplo...\n")
    
    try:
        from statsbombpy import sb
        import pandas as pd
        
        # Cargar datos de un solo partido (la final)
        # Argentina vs Francia, Final del Mundial 2022
        
        matches = sb.matches(competition_id=43, season_id=106)
        final = matches[
            (matches['home_team'].isin(['Argentina', 'France'])) & 
            (matches['away_team'].isin(['Argentina', 'France']))
        ].sort_values('match_date').iloc[-1]
        
        match_id = final['match_id']
        print(f"   Partido: {final['home_team']} vs {final['away_team']}")
        print(f"   Match ID: {match_id}")
        
        # Cargar eventos
        events = sb.events(match_id=match_id)
        passes = events[events['type'] == 'Pass'].copy()
        passes['match_id'] = match_id
        
        # Cargar frames
        frames = sb.frames(match_id=match_id)
        frames['match_id'] = match_id
        
        # Unir datos
        passes_with_ff = passes.merge(
            frames[['id', 'freeze_frame', 'visible_area']],
            on='id',
            how='left'
        )
        
        # Guardar
        passes_with_ff.to_pickle('data/processed/sample_passes.pkl')
        
        print(f"\n   ✅ Pases guardados: {len(passes_with_ff)}")
        print(f"   ✅ Con freeze frame: {passes_with_ff['freeze_frame'].notna().sum()}")
        print(f"   📍 Archivo: data/processed/sample_passes.pkl")
        
        print("\n✅ Datos de ejemplo descargados correctamente\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error descargando datos: {e}")
        return False


def run_quick_analysis():
    """Ejecuta un análisis rápido de ejemplo."""
    print("📊 Ejecutando análisis de ejemplo...\n")
    
    try:
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        from mplsoccer import Pitch
        
        # Cargar datos
        passes = pd.read_pickle('data/processed/sample_passes.pkl')
        
        # Extraer coordenadas
        passes['start_x'] = passes['location'].apply(lambda x: x[0] if isinstance(x, list) else np.nan)
        passes['start_y'] = passes['location'].apply(lambda x: x[1] if isinstance(x, list) else np.nan)
        passes['end_x'] = passes['pass_end_location'].apply(lambda x: x[0] if isinstance(x, list) else np.nan)
        passes['end_y'] = passes['pass_end_location'].apply(lambda x: x[1] if isinstance(x, list) else np.nan)
        passes['success'] = passes['pass_outcome'].isna().astype(int)
        
        # Estadísticas
        print(f"   Total de pases: {len(passes)}")
        print(f"   Tasa de completados: {passes['success'].mean()*100:.1f}%")
        print(f"   Distancia media: {passes['pass_length'].mean():.1f} unidades")
        
        # Crear pass map
        argentina_passes = passes[passes['team'] == 'Argentina']
        completed = argentina_passes[argentina_passes['success'] == 1]
        incomplete = argentina_passes[argentina_passes['success'] == 0]
        
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='white')
        fig, ax = pitch.draw(figsize=(12, 8))
        
        pitch.arrows(completed['start_x'], completed['start_y'],
                     completed['end_x'], completed['end_y'],
                     width=2, headwidth=5, headlength=5,
                     color='#2A9D8F', alpha=0.6, ax=ax,
                     label=f'Completados ({len(completed)})')
        
        pitch.arrows(incomplete['start_x'], incomplete['start_y'],
                     incomplete['end_x'], incomplete['end_y'],
                     width=2, headwidth=5, headlength=5,
                     color='#E63946', alpha=0.6, ax=ax,
                     label=f'Fallados ({len(incomplete)})')
        
        ax.set_title('Pass Map: Argentina - Final Mundial 2022',
                     fontsize=14, fontweight='bold', color='white')
        ax.legend(loc='upper left')
        
        plt.savefig('outputs/figures/sample_passmap.png', dpi=150, 
                    bbox_inches='tight', facecolor='#22312b')
        plt.close()
        
        print(f"\n   ✅ Pass map guardado: outputs/figures/sample_passmap.png")
        print("\n✅ Análisis de ejemplo completado\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en análisis: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal."""
    print("=" * 60)
    print("⚽ FOOTBALL ANALYTICS - OART PROJECT")
    print("   Quick Start Script")
    print("=" * 60)
    print()
    
    # 1. Verificar dependencias
    if not check_dependencies():
        print("❌ Por favor instala las dependencias faltantes y vuelve a ejecutar.")
        sys.exit(1)
    
    # 2. Crear directorios
    create_directories()
    
    # 3. Probar conexión
    if not test_statsbomb_connection():
        print("❌ No se pudo conectar con StatsBomb.")
        sys.exit(1)
    
    # 4. Descargar datos de ejemplo
    if not load_sample_data():
        print("❌ Error descargando datos.")
        sys.exit(1)
    
    # 5. Análisis de ejemplo
    if not run_quick_analysis():
        print("⚠️ El análisis de ejemplo falló, pero puedes continuar manualmente.")
    
    # Resumen
    print("=" * 60)
    print("✅ SETUP COMPLETADO")
    print("=" * 60)
    print("""
Próximos pasos:
    
1. Abre Jupyter Notebook:
   $ jupyter notebook notebooks/
   
2. Ejecuta los notebooks en orden:
   - 01_data_exploration.ipynb
   - 02_pass_success_model.ipynb
   - 03_oart_calculation.ipynb
   
3. O ejecuta el análisis completo:
   $ python run_full_analysis.py

¡Buena suerte con tu proyecto de football analytics! ⚽📊
""")


if __name__ == "__main__":
    main()
