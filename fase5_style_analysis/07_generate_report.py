"""
Generar reporte de análisis táctico con IA.
Combina todos los datos recopilados en un reporte profesional.
"""

import json
import pandas as pd
from datetime import datetime

print("=" * 60)
print("📝 GENERANDO REPORTE CON IA")
print("=" * 60)

# ============================================================
# PASO 1: Cargar todos los datos
# ============================================================

print("\n📥 Cargando datos...")

# Comparación de estilos de equipo
style_comparison = pd.read_csv('data/style_comparison.csv', index_col=0)

# Comparación Messi vs Mbappé
messi_mbappe = pd.read_csv('data/messi_vs_mbappe.csv', index_col=0)

# Resultados OART
with open('data/oart_results.json', 'r') as f:
    oart_results = json.load(f)

print("✅ Datos cargados")

# ============================================================
# PASO 2: Estructurar datos para el reporte
# ============================================================

# Convertir DataFrames a diccionarios
style_data = style_comparison.to_dict()
player_data = messi_mbappe.to_dict()

# Crear resumen estructurado
report_data = {
    "tournament": "Mundial Qatar 2022",
    "teams_analyzed": ["Argentina", "Francia"],
    "final_result": "Argentina 3-3 Francia (4-2 en penales)",
    
    "team_comparison": {
        "argentina": {
            "style": "Control + Eficiencia",
            "goals": 23,
            "xg": 20.99,
            "pass_accuracy": 85.4,
            "pressing_per_game": 140,
            "main_attack_side": "Derecha (37.8%)",
            "key_strength": "Creación de ocasiones y eficiencia",
            "weakness": "Dependencia de Messi"
        },
        "france": {
            "style": "Transición + Talento Individual",
            "goals": 18,
            "xg": 14.96,
            "pass_accuracy": 83.8,
            "pressing_per_game": 129.3,
            "main_attack_side": "Izquierda (36.6%)",
            "key_strength": "Goles de alta dificultad (+3 sobre xG)",
            "weakness": "Dependencia de Mbappé"
        }
    },
    
    "player_comparison": {
        "messi": {
            "goals": 9,
            "assists": 3,
            "key_passes": 16,
            "progressive_passes": 110,
            "dribble_success": "72.2%",
            "xg": 7.6,
            "goals_over_xg": 1.4,
            "oart": oart_results['messi']['oart_mean'],
            "role": "Creador y finalizador"
        },
        "mbappe": {
            "goals": 9,
            "assists": 2,
            "key_passes": 9,
            "progressive_passes": 44,
            "dribble_success": "60.0%",
            "xg": 5.02,
            "goals_over_xg": 3.98,
            "oart": oart_results['mbappe']['oart_mean'],
            "role": "Goleador explosivo"
        }
    },
    
    "oart_analysis": {
        "messi_oart": round(oart_results['messi']['oart_mean'], 3),
        "mbappe_oart": round(oart_results['mbappe']['oart_mean'], 3),
        "interpretation": "Ambos son jugadores arriesgados (OART > 0.5)",
        "messi_passes_analyzed": oart_results['messi']['passes_analyzed'],
        "mbappe_passes_analyzed": oart_results['mbappe']['passes_analyzed']
    }
}

# ============================================================
# PASO 3: Generar reporte en formato Markdown
# ============================================================

print("\n📝 Generando reporte...")

report_md = f"""# ⚽ Análisis Táctico: Final Mundial Qatar 2022
## Argentina vs Francia

**Fecha del análisis:** {datetime.now().strftime("%d de %B, %Y")}  
**Analista:** Sistema de Análisis Táctico con IA  
**Fuente de datos:** StatsBomb Open Data (360°)

---

## 📋 Resumen Ejecutivo

La final del Mundial Qatar 2022 enfrentó a dos equipos con filosofías opuestas pero igualmente efectivas. **Argentina** llegó como un equipo colectivo con alta precisión de pase y pressing intenso, mientras que **Francia** dependía de transiciones rápidas y el talento individual de Mbappé.

El partido terminó **3-3** en tiempo reglamentario, con Argentina ganando **4-2 en penales**. Fue considerada una de las mejores finales en la historia de los mundiales.

### Datos Clave del Torneo

| Métrica | Argentina 🇦🇷 | Francia 🇫🇷 |
|---------|---------------|-------------|
| Goles | 23 | 18 |
| xG Total | 20.99 | 14.96 |
| Precisión de Pase | 85.4% | 83.8% |
| Pressing/Partido | 140 | 129.3 |

---

## 🎯 Análisis de Estilo de Juego

### Argentina: Control + Eficiencia

Argentina bajo Scaloni mostró un estilo basado en:

1. **Alta posesión con propósito** - No solo tener el balón, sino progresar
2. **Pressing alto** - 140 presiones por partido, recuperando en zona alta el 45.5% de las veces
3. **Ataque por banda derecha** - 37.8% de sus acciones, aprovechando a Di María y Molina
4. **Eficiencia clínica** - 20.9% de conversión de tiros a gol

**Fortaleza principal:** Creaban más ocasiones que cualquier otro equipo (xG 21) y las convertían.

**Debilidad:** Dependencia extrema de Messi para la creatividad.

### Francia: Transición + Talento

Francia de Deschamps jugó un estilo diferente:

1. **Juego directo** - 18.4% de pases largos, más que Argentina
2. **Verticalidad extrema** - 31.2% de pases progresivos
3. **Ataque por izquierda** - 36.6%, con Theo Hernández subiendo y Mbappé cortando
4. **Goles "imposibles"** - +3.04 goles sobre xG esperado

**Fortaleza principal:** Capacidad de ganar partidos con momentos de brillantez individual.

**Debilidad:** Cuando Mbappé no aparecía, el equipo sufría creativamente.

---

## 👥 Duelo Estelar: Messi vs Mbappé

Los dos mejores jugadores del torneo tuvieron actuaciones históricas.

### Comparación Directa

| Métrica | Messi 🇦🇷 | Mbappé 🇫🇷 | Ventaja |
|---------|-----------|------------|---------|
| Goles | 9 | 9 | Empate |
| Asistencias | 3 | 2 | Messi |
| G + A | 12 | 11 | Messi |
| xG | 7.6 | 5.02 | Messi |
| Goles sobre xG | +1.4 | +3.98 | Mbappé |
| Pases Clave | 16 | 9 | Messi |
| Regates Exitosos | 26/36 (72%) | 30/50 (60%) | Messi |
| Pases Progresivos | 110 | 44 | Messi |

### Análisis OART (Toma de Riesgos en Pases)

Utilizando nuestra métrica **OART (Opportunity-Adjusted Risk Taking)**, medimos qué tan arriesgados son los pases de cada jugador comparados con las alternativas disponibles:

| Jugador | OART | Interpretación |
|---------|------|----------------|
| Messi | **{report_data['oart_analysis']['messi_oart']}** | Arriesgado |
| Mbappé | **{report_data['oart_analysis']['mbappe_oart']}** | Arriesgado |

**Hallazgo clave:** Ambos jugadores tienen OART prácticamente idéntico (~0.57), lo que significa que:
- Eligen pases difíciles el 57% de las veces cuando tienen opciones más fáciles
- Son jugadores que buscan el riesgo para crear desequilibrio
- La diferencia está en el TIPO de riesgo: Messi busca el pase filtrado, Mbappé busca el regate y disparo

### Perfiles de Jugador

**Lionel Messi - El Director de Orquesta**
- Posición promedio: Centro-derecha, bajando a buscar el balón
- Más acciones totales (1,553 vs 1,110)
- Mejor creador del torneo (16 pases clave)
- Regates más efectivos (72% vs 60%)
- Rol: Organizador + Finalizador

**Kylian Mbappé - El Depredador**
- Posición promedio: Banda izquierda, muy adelantado
- Más letal frente al gol (+3.98 sobre xG)
- Más regates intentados (50 vs 36)
- Dependencia total del gol como contribución
- Rol: Finalizador puro

---

## 📊 Métricas Avanzadas

### Expected Goals (xG)

| Equipo | xG Total | Goles Reales | Diferencia |
|--------|----------|--------------|------------|
| Argentina | 20.99 | 23 | +2.01 |
| Francia | 14.96 | 18 | +3.04 |

Ambos equipos sobre-rindieron su xG, pero Francia lo hizo de manera más dramática, indicando mayor dependencia de goles de alta dificultad.

### Zonas de Ataque

**Argentina:**
- Banda derecha: 37.8%
- Centro: 31.5%
- Banda izquierda: 30.6%

**Francia:**
- Banda izquierda: 36.6%
- Banda derecha: 35.3%
- Centro: 28.1%

---

## 💡 Conclusiones y Recomendaciones

### Para enfrentar a Argentina:
1. **No presionar alto** - Su precisión de pase (85.4%) les permite salir fácilmente
2. **Cerrar la banda derecha** - Es su zona preferida de ataque
3. **Doblar marca a Messi** - Es el único creador real del equipo
4. **Aprovechar transiciones** - Cuando pierden el balón, tardan en reorganizarse

### Para enfrentar a Francia:
1. **Mantener el balón** - Son letales en transiciones
2. **Forzar a Mbappé hacia adentro** - Es menos efectivo cortando al centro
3. **Presionar a Tchouaméni** - Es el único enlace entre defensa y ataque
4. **No dejar espacios a la espalda** - Mbappé tiene velocidad élite

### Lección táctica del torneo:
> "No hay un solo camino hacia el éxito. Argentina ganó con control y colectivo. Francia casi gana con explosividad individual. Lo importante es maximizar las fortalezas propias."

---

## 📎 Metodología

Este análisis fue realizado utilizando:
- **Datos:** StatsBomb Open Data con información 360° (posiciones de todos los jugadores)
- **Modelo de pases:** Gradient Boosting con AUC = 0.893
- **OART:** Métrica propia basada en el paper "Quantifying Opportunity-Adjusted Risk Taking in Football Pass Selection"
- **Visualizaciones:** Matplotlib, mapas de calor, gráficos radar
- **Eventos analizados:** 49,614 eventos totales, 673,067 frames 360°

---

*Reporte generado automáticamente por el Sistema de Análisis Táctico*  
*{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

# Guardar reporte en Markdown
with open('outputs/tactical_report.md', 'w', encoding='utf-8') as f:
    f.write(report_md)

print("✅ Reporte guardado: outputs/tactical_report.md")

# ============================================================
# PASO 4: Convertir a HTML para mejor visualización
# ============================================================

html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis Táctico - Mundial 2022</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        
        h1 {{
            color: #1a1a2e;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        
        h2 {{
            color: #16213e;
            margin-top: 30px;
            margin-bottom: 15px;
            border-left: 4px solid #4CAF50;
            padding-left: 10px;
        }}
        
        h3 {{
            color: #1a1a2e;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        th {{
            background: #1a1a2e;
            color: white;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        .highlight {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        
        .metric-box {{
            display: inline-block;
            background: white;
            padding: 15px 25px;
            margin: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #4CAF50;
        }}
        
        .metric-label {{
            font-size: 0.9em;
            color: #666;
        }}
        
        blockquote {{
            border-left: 4px solid #4CAF50;
            padding-left: 20px;
            margin: 20px 0;
            font-style: italic;
            color: #555;
        }}
        
        .team-argentina {{
            color: #75AADB;
        }}
        
        .team-france {{
            color: #002654;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>⚽ Análisis Táctico: Final Mundial Qatar 2022</h1>
    <h2>Argentina vs Francia</h2>
    
    <p><strong>Fecha del análisis:</strong> {datetime.now().strftime("%d de %B, %Y")}<br>
    <strong>Fuente de datos:</strong> StatsBomb Open Data (360°)</p>
    
    <div class="highlight">
        <h3>📋 Resumen Ejecutivo</h3>
        <p>Argentina ganó la final 4-2 en penales después de un épico 3-3. 
        Dos estilos opuestos: el control argentino vs la explosividad francesa.</p>
    </div>
    
    <div style="text-align: center; margin: 30px 0;">
        <div class="metric-box">
            <div class="metric-value team-argentina">23</div>
            <div class="metric-label">Goles Argentina</div>
        </div>
        <div class="metric-box">
            <div class="metric-value team-france">18</div>
            <div class="metric-label">Goles Francia</div>
        </div>
        <div class="metric-box">
            <div class="metric-value">0.893</div>
            <div class="metric-label">AUC Modelo</div>
        </div>
    </div>
    
    <h2>🎯 Comparación de Estilos</h2>
    
    <table>
        <tr>
            <th>Métrica</th>
            <th class="team-argentina">Argentina 🇦🇷</th>
            <th class="team-france">Francia 🇫🇷</th>
        </tr>
        <tr>
            <td>Estilo</td>
            <td>Control + Eficiencia</td>
            <td>Transición + Talento</td>
        </tr>
        <tr>
            <td>xG Total</td>
            <td>20.99</td>
            <td>14.96</td>
        </tr>
        <tr>
            <td>Precisión Pase</td>
            <td>85.4%</td>
            <td>83.8%</td>
        </tr>
        <tr>
            <td>Pressing/Partido</td>
            <td>140</td>
            <td>129.3</td>
        </tr>
        <tr>
            <td>Zona de Ataque</td>
            <td>Derecha (37.8%)</td>
            <td>Izquierda (36.6%)</td>
        </tr>
    </table>
    
    <h2>👥 Messi vs Mbappé</h2>
    
    <table>
        <tr>
            <th>Métrica</th>
            <th>Messi 🇦🇷</th>
            <th>Mbappé 🇫🇷</th>
        </tr>
        <tr>
            <td>Goles</td>
            <td>9</td>
            <td>9</td>
        </tr>
        <tr>
            <td>Asistencias</td>
            <td>3</td>
            <td>2</td>
        </tr>
        <tr>
            <td>xG</td>
            <td>7.6</td>
            <td>5.02</td>
        </tr>
        <tr>
            <td>Sobre xG</td>
            <td>+1.4</td>
            <td>+3.98</td>
        </tr>
        <tr>
            <td>Pases Clave</td>
            <td>16</td>
            <td>9</td>
        </tr>
        <tr>
            <td><strong>OART</strong></td>
            <td><strong>{report_data['oart_analysis']['messi_oart']}</strong></td>
            <td><strong>{report_data['oart_analysis']['mbappe_oart']}</strong></td>
        </tr>
    </table>
    
    <h2>📊 Análisis OART</h2>
    
    <p>El <strong>OART (Opportunity-Adjusted Risk Taking)</strong> mide qué tan arriesgados 
    son los pases de un jugador comparados con las alternativas disponibles.</p>
    
    <div style="text-align: center; margin: 20px 0;">
        <div class="metric-box">
            <div class="metric-value">{report_data['oart_analysis']['messi_oart']}</div>
            <div class="metric-label">OART Messi</div>
        </div>
        <div class="metric-box">
            <div class="metric-value">{report_data['oart_analysis']['mbappe_oart']}</div>
            <div class="metric-label">OART Mbappé</div>
        </div>
    </div>
    
    <p><strong>Interpretación:</strong> Ambos jugadores son "arriesgados" (OART > 0.5), 
    eligiendo pases difíciles el ~57% de las veces cuando tenían opciones más fáciles.</p>
    
    <h2>💡 Conclusiones</h2>
    
    <blockquote>
        "No hay un solo camino hacia el éxito. Argentina ganó con control y colectivo. 
        Francia casi gana con explosividad individual. Lo importante es maximizar las fortalezas propias."
    </blockquote>
    
    <div class="footer">
        <p>Reporte generado automáticamente por el Sistema de Análisis Táctico<br>
        {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
</body>
</html>
"""

# Guardar HTML
with open('outputs/tactical_report.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("✅ Reporte HTML guardado: outputs/tactical_report.html")

print("\n" + "=" * 60)
print("✅ REPORTES GENERADOS")
print("=" * 60)
print("\nArchivos creados:")
print("   📄 outputs/tactical_report.md   - Formato Markdown")
print("   🌐 outputs/tactical_report.html - Formato Web")
print("\nAbre el archivo HTML en tu navegador para ver el reporte completo.")