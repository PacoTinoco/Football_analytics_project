"""
Visualizar estilos de juego de Argentina y Francia.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi

# Cargar datos
comparison = pd.read_csv('data/style_comparison.csv', index_col=0)

print("=" * 60)
print("📊 VISUALIZANDO ESTILOS DE JUEGO")
print("=" * 60)

# Colores de los equipos
ARGENTINA_COLOR = '#75AADB'  # Celeste
FRANCE_COLOR = '#002654'     # Azul oscuro

# ============================================================
# 1. RADAR CHART - Comparación general
# ============================================================

def create_radar_chart():
    """Crea gráfico de radar comparando métricas clave."""
    
    # Métricas para el radar (normalizadas manualmente para comparación)
    categories = [
        'Precisión\nPases', 
        'Verticalidad', 
        'Pressing', 
        'Eficiencia\nGol',
        'Regates',
        'xG Creado'
    ]
    
    # Valores (normalizados a escala 0-100)
    argentina_values = [
        85.4,           # pass_accuracy
        28.3 * 2.5,     # progressive_passes_pct (escalado)
        140 / 2,        # pressures_per_game (escalado)
        20.9 * 4,       # conversion_rate (escalado)
        54.1,           # dribble_success_rate
        20.99 * 4       # total_xg (escalado)
    ]
    
    france_values = [
        83.8,           # pass_accuracy
        31.2 * 2.5,     # progressive_passes_pct
        129.3 / 2,      # pressures_per_game
        17.0 * 4,       # conversion_rate
        59.2,           # dribble_success_rate
        14.96 * 4       # total_xg
    ]
    
    # Número de variables
    num_vars = len(categories)
    
    # Ángulos para cada eje
    angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
    angles += angles[:1]  # Cerrar el círculo
    
    # Valores (cerrar el círculo)
    argentina_values += argentina_values[:1]
    france_values += france_values[:1]
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    # Dibujar Argentina
    ax.plot(angles, argentina_values, 'o-', linewidth=2, 
            label='Argentina 🇦🇷', color=ARGENTINA_COLOR)
    ax.fill(angles, argentina_values, alpha=0.25, color=ARGENTINA_COLOR)
    
    # Dibujar Francia
    ax.plot(angles, france_values, 'o-', linewidth=2, 
            label='Francia 🇫🇷', color=FRANCE_COLOR)
    ax.fill(angles, france_values, alpha=0.25, color=FRANCE_COLOR)
    
    # Configurar ejes
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=12)
    ax.set_ylim(0, 100)
    
    plt.title('Comparación de Estilos de Juego\nMundial 2022', 
              size=16, fontweight='bold', y=1.08)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    
    plt.tight_layout()
    plt.savefig('outputs/radar_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Guardado: outputs/radar_comparison.png")

# ============================================================
# 2. BARRAS COMPARATIVAS
# ============================================================

def create_bar_comparison():
    """Crea gráfico de barras comparativo."""
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Datos
    metrics_groups = {
        'Posesión': {
            'Precisión Pases (%)': [85.4, 83.8],
            'Pases Progresivos (%)': [28.3, 31.2],
            'Pases Largos (%)': [15.6, 18.4],
            'Pases Cortos (%)': [44.2, 41.7]
        },
        'Ataque': {
            'Tiros/Partido': [15.7, 15.1],
            'Conversión (%)': [20.9, 17.0],
            'xG/Partido': [3.0, 2.14],
            'Pases al Área/Partido': [33.6, 35.1]
        },
        'Pressing': {
            'Presiones/Partido': [140.0, 129.3],
            'Recuperaciones': [325, 310],
            'Recup. Zona Alta (%)': [45.5, 44.8]
        },
        'Lateralidad': {
            'Banda Izquierda (%)': [30.6, 36.6],
            'Centro (%)': [31.5, 28.1],
            'Banda Derecha (%)': [37.8, 35.3]
        }
    }
    
    for idx, (group_name, metrics) in enumerate(metrics_groups.items()):
        ax = axes[idx // 2, idx % 2]
        
        labels = list(metrics.keys())
        arg_vals = [v[0] for v in metrics.values()]
        fra_vals = [v[1] for v in metrics.values()]
        
        x = np.arange(len(labels))
        width = 0.35
        
        bars1 = ax.barh(x - width/2, arg_vals, width, label='Argentina', 
                        color=ARGENTINA_COLOR, alpha=0.8)
        bars2 = ax.barh(x + width/2, fra_vals, width, label='Francia', 
                        color=FRANCE_COLOR, alpha=0.8)
        
        ax.set_yticks(x)
        ax.set_yticklabels(labels)
        ax.set_title(group_name, fontweight='bold', fontsize=12)
        ax.legend()
        
        # Añadir valores en las barras
        for bar, val in zip(bars1, arg_vals):
            ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, 
                   f'{val}', va='center', fontsize=9)
        for bar, val in zip(bars2, fra_vals):
            ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, 
                   f'{val}', va='center', fontsize=9)
    
    plt.suptitle('Métricas Detalladas por Categoría - Mundial 2022', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('outputs/bar_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Guardado: outputs/bar_comparison.png")

# ============================================================
# 3. GRÁFICO DE EFICIENCIA (xG vs Goles)
# ============================================================

def create_efficiency_chart():
    """Muestra xG vs Goles reales."""
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Datos
    teams = ['Argentina', 'Francia']
    xg = [20.99, 14.96]
    goals = [23, 18]
    colors = [ARGENTINA_COLOR, FRANCE_COLOR]
    
    # Scatter plot
    for i, team in enumerate(teams):
        ax.scatter(xg[i], goals[i], s=500, c=colors[i], 
                  label=f'{team}', edgecolors='black', linewidth=2, zorder=5)
        ax.annotate(f'{team}\nxG: {xg[i]}\nGoles: {goals[i]}', 
                   (xg[i], goals[i]), textcoords="offset points", 
                   xytext=(20, 0), ha='left', fontsize=11)
    
    # Línea de referencia (xG = Goles)
    min_val = min(min(xg), min(goals)) - 2
    max_val = max(max(xg), max(goals)) + 2
    ax.plot([min_val, max_val], [min_val, max_val], 'k--', 
            alpha=0.5, label='Rendimiento esperado')
    
    # Zonas
    ax.fill_between([min_val, max_val], [min_val, max_val], max_val,
                    alpha=0.1, color='green', label='Sobre-rendimiento')
    ax.fill_between([min_val, max_val], min_val, [min_val, max_val],
                    alpha=0.1, color='red', label='Bajo-rendimiento')
    
    ax.set_xlabel('Expected Goals (xG)', fontsize=12)
    ax.set_ylabel('Goles Reales', fontsize=12)
    ax.set_title('Eficiencia Goleadora - Mundial 2022\n¿Quién convirtió más de lo esperado?', 
                fontsize=14, fontweight='bold')
    ax.legend(loc='lower right')
    ax.set_xlim(min_val, max_val)
    ax.set_ylim(min_val, max_val)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('outputs/efficiency_chart.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Guardado: outputs/efficiency_chart.png")

# ============================================================
# 4. RESUMEN VISUAL DE ESTILOS
# ============================================================

def create_style_summary():
    """Crea un resumen visual del estilo de cada equipo."""
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    teams_data = [
        {
            'name': 'ARGENTINA 🇦🇷',
            'color': ARGENTINA_COLOR,
            'style': 'CONTROL + EFICIENCIA',
            'traits': [
                '✓ Alta precisión de pase (85.4%)',
                '✓ Pressing intenso (140/partido)',
                '✓ Muy eficientes (20.9% conversión)',
                '✓ Ataque por derecha (37.8%)',
                '✓ Crearon más ocasiones (xG 21)',
                '✓ Recuperación alta (45.5%)'
            ],
            'key_insight': 'Equipo completo que controlaba\npartidos y era letal en el área'
        },
        {
            'name': 'FRANCIA 🇫🇷',
            'color': FRANCE_COLOR,
            'style': 'TRANSICIÓN + TALENTO',
            'traits': [
                '✓ Juego más directo (18.4% largos)',
                '✓ Muy verticales (31.2% progresivos)',
                '✓ Mejores regateadores (59.2%)',
                '✓ Ataque por izquierda (36.6%)',
                '✓ Goles "imposibles" (+3 sobre xG)',
                '✓ Dependen de individualidades'
            ],
            'key_insight': 'Equipo de transiciones rápidas\ny genialidades de Mbappé'
        }
    ]
    
    for idx, team in enumerate(teams_data):
        ax = axes[idx]
        ax.set_facecolor('#f5f5f5')
        
        # Título
        ax.text(0.5, 0.95, team['name'], transform=ax.transAxes,
               fontsize=20, fontweight='bold', ha='center', va='top',
               color=team['color'])
        
        # Estilo
        ax.text(0.5, 0.85, team['style'], transform=ax.transAxes,
               fontsize=14, ha='center', va='top',
               style='italic', color='gray')
        
        # Características
        y_pos = 0.72
        for trait in team['traits']:
            ax.text(0.1, y_pos, trait, transform=ax.transAxes,
                   fontsize=12, ha='left', va='top')
            y_pos -= 0.08
        
        # Insight clave
        ax.text(0.5, 0.15, team['key_insight'], transform=ax.transAxes,
               fontsize=13, ha='center', va='top',
               fontweight='bold', color=team['color'],
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    
    plt.suptitle('Resumen de Estilos de Juego - Final Mundial 2022', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('outputs/style_summary.png', dpi=150, bbox_inches='tight', 
                facecolor='white')
    plt.close()
    print("✅ Guardado: outputs/style_summary.png")

# ============================================================
# EJECUTAR TODAS LAS VISUALIZACIONES
# ============================================================

print("\n⏳ Generando visualizaciones...")

create_radar_chart()
create_bar_comparison()
create_efficiency_chart()
create_style_summary()

print("\n" + "=" * 60)
print("✅ TODAS LAS VISUALIZACIONES GENERADAS")
print("=" * 60)
print("\nArchivos creados en 'outputs/':")
print("   • radar_comparison.png   - Comparación general")
print("   • bar_comparison.png     - Métricas detalladas")
print("   • efficiency_chart.png   - xG vs Goles")
print("   • style_summary.png      - Resumen de estilos")