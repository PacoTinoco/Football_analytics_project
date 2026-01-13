"""
Calcular OART (Opportunity-Adjusted Risk Taking) para Messi y Mbappé.
Usando datos 360° del Mundial 2022.
"""

import pandas as pd
import numpy as np
from statsbombpy import sb
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score
import warnings
import json

warnings.filterwarnings('ignore')

print("=" * 60)
print("📊 CALCULANDO OART - MESSI vs MBAPPÉ")
print("=" * 60)

# Cargar IDs de partidos
with open('data/worldcup_matches.json', 'r') as f:
    match_data = json.load(f)

# Combinar todos los IDs únicos
all_match_ids = list(set(match_data['argentina_match_ids'] + match_data['france_match_ids']))

print(f"\n📥 Cargando datos de {len(all_match_ids)} partidos...")

# ============================================================
# PASO 1: Cargar eventos y frames 360
# ============================================================

all_events = []
all_frames = []

for match_id in all_match_ids:
    try:
        # Eventos
        events = sb.events(match_id=match_id)
        events['match_id'] = match_id
        all_events.append(events)
        
        # Frames 360
        frames = sb.frames(match_id=match_id)
        frames['match_id'] = match_id
        all_frames.append(frames)
    except Exception as e:
        print(f"   Error en partido {match_id}: {e}")
        continue

events_df = pd.concat(all_events, ignore_index=True)
frames_df = pd.concat(all_frames, ignore_index=True)

print(f"✅ Eventos cargados: {len(events_df):,}")
print(f"✅ Frames 360 cargados: {len(frames_df):,}")

# ============================================================
# PASO 2: Filtrar pases y preparar datos
# ============================================================

# Solo pases
passes = events_df[events_df['type'] == 'Pass'].copy()

# Filtrar pases de Messi y Mbappé
messi_passes = passes[passes['player'].str.contains('Messi', na=False)].copy()
mbappe_passes = passes[passes['player'].str.contains('Mbappé', na=False)].copy()

print(f"\n📊 Pases encontrados:")
print(f"   Messi: {len(messi_passes)}")
print(f"   Mbappé: {len(mbappe_passes)}")

# ============================================================
# PASO 3: Reconstruir freeze frames por evento
# ============================================================

print("\n⏳ Procesando freeze frames...")

# Agrupar frames por evento
def get_freeze_frame(event_id, frames):
    """Obtiene el freeze frame para un evento específico."""
    event_frames = frames[frames['id'] == event_id]
    if len(event_frames) == 0:
        return None
    
    teammates = []
    opponents = []
    
    for _, row in event_frames.iterrows():
        player_info = {
            'location': row['location'] if isinstance(row['location'], list) else None,
            'teammate': row.get('teammate', None),
            'actor': row.get('actor', False),
            'keeper': row.get('keeper', False)
        }
        
        if player_info['location'] is not None:
            if row.get('teammate', False):
                teammates.append(player_info)
            else:
                opponents.append(player_info)
    
    return {'teammates': teammates, 'opponents': opponents}

# ============================================================
# PASO 4: Extraer features para el modelo de pases
# ============================================================

def extract_pass_features(row, receiver_loc=None):
    """
    Extrae características de un pase para predecir éxito.
    
    Si receiver_loc es None, usa la ubicación real del receptor.
    Si se proporciona, calcula features para esa ubicación alternativa.
    """
    features = {}
    
    try:
        # Ubicación del pasador
        start_loc = row['location']
        if not isinstance(start_loc, list):
            return None
        
        # Ubicación del receptor (real o alternativa)
        if receiver_loc is not None:
            end_loc = receiver_loc
        else:
            end_loc = row.get('pass_end_location')
            if not isinstance(end_loc, list):
                return None
        
        # Distancia del pase
        features['pass_distance'] = np.sqrt(
            (end_loc[0] - start_loc[0])**2 + 
            (end_loc[1] - start_loc[1])**2
        )
        
        # Ángulo del pase
        features['pass_angle'] = np.arctan2(
            end_loc[1] - start_loc[1],
            end_loc[0] - start_loc[0]
        )
        
        # Posición inicial (x, y)
        features['start_x'] = start_loc[0]
        features['start_y'] = start_loc[1]
        
        # Posición final
        features['end_x'] = end_loc[0]
        features['end_y'] = end_loc[1]
        
        # ¿Es pase progresivo?
        features['is_progressive'] = 1 if end_loc[0] > start_loc[0] + 10 else 0
        
        # ¿Es pase al área?
        features['is_to_box'] = 1 if (end_loc[0] > 102 and 18 < end_loc[1] < 62) else 0
        
        # Distancia al gol desde destino
        features['end_distance_to_goal'] = np.sqrt(
            (120 - end_loc[0])**2 + (40 - end_loc[1])**2
        )
        
        # ¿Bajo presión?
        features['under_pressure'] = 1 if row.get('under_pressure', False) else 0
        
        return features
        
    except Exception as e:
        return None

# ============================================================
# PASO 5: Entrenar modelo de predicción de pases
# ============================================================

print("\n⏳ Entrenando modelo de predicción de pases...")

# Preparar datos de entrenamiento (todos los pases del torneo)
training_data = []

for _, row in passes.iterrows():
    features = extract_pass_features(row)
    if features is not None:
        # Outcome: 1 si el pase fue exitoso, 0 si falló
        outcome = 0 if pd.notna(row.get('pass_outcome')) else 1
        features['outcome'] = outcome
        training_data.append(features)

train_df = pd.DataFrame(training_data)

print(f"   Datos de entrenamiento: {len(train_df):,} pases")

# Features y target
feature_cols = ['pass_distance', 'pass_angle', 'start_x', 'start_y', 
                'end_x', 'end_y', 'is_progressive', 'is_to_box',
                'end_distance_to_goal', 'under_pressure']

X = train_df[feature_cols]
y = train_df['outcome']

# Entrenar modelo
model = GradientBoostingClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)

# Validación cruzada
cv_scores = cross_val_score(model, X, y, cv=5, scoring='roc_auc')
print(f"   AUC (validación cruzada): {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

# Entrenar modelo final
model.fit(X, y)
print("✅ Modelo entrenado")

# ============================================================
# PASO 6: Calcular OART para cada jugador
# ============================================================

def calculate_player_oart(player_passes, frames_df, model, feature_cols):
    """
    Calcula OART para un jugador.
    
    Para cada pase:
    1. Obtener freeze frame (posiciones de compañeros)
    2. Predecir probabilidad de éxito del pase real
    3. Predecir probabilidad para cada alternativa
    4. OART = % de alternativas con mayor probabilidad
    """
    oart_scores = []
    pass_details = []
    
    for _, row in player_passes.iterrows():
        try:
            # Obtener freeze frame
            freeze_frame = get_freeze_frame(row['id'], frames_df)
            
            if freeze_frame is None or len(freeze_frame['teammates']) < 2:
                continue
            
            # Features del pase real
            real_features = extract_pass_features(row)
            if real_features is None:
                continue
            
            # Probabilidad del pase real
            real_X = pd.DataFrame([real_features])[feature_cols]
            real_prob = model.predict_proba(real_X)[0][1]
            
            # Calcular probabilidad para cada alternativa
            alternative_probs = []
            
            for teammate in freeze_frame['teammates']:
                if teammate['actor']:  # Saltar al pasador mismo
                    continue
                if teammate['location'] is None:
                    continue
                
                # Features para pase alternativo
                alt_features = extract_pass_features(row, receiver_loc=teammate['location'])
                if alt_features is None:
                    continue
                
                alt_X = pd.DataFrame([alt_features])[feature_cols]
                alt_prob = model.predict_proba(alt_X)[0][1]
                alternative_probs.append(alt_prob)
            
            if len(alternative_probs) == 0:
                continue
            
            # OART = proporción de alternativas con mayor probabilidad
            better_alternatives = sum(1 for p in alternative_probs if p > real_prob)
            oart = better_alternatives / len(alternative_probs)
            
            oart_scores.append(oart)
            
            # Guardar detalles
            pass_details.append({
                'event_id': row['id'],
                'real_prob': real_prob,
                'num_alternatives': len(alternative_probs),
                'better_alternatives': better_alternatives,
                'oart': oart,
                'pass_successful': 1 if pd.isna(row.get('pass_outcome')) else 0,
                'pass_distance': real_features['pass_distance'],
                'is_progressive': real_features['is_progressive']
            })
            
        except Exception as e:
            continue
    
    return oart_scores, pass_details

print("\n⏳ Calculando OART para Messi...")
messi_oart_scores, messi_details = calculate_player_oart(
    messi_passes, frames_df, model, feature_cols
)

print("⏳ Calculando OART para Mbappé...")
mbappe_oart_scores, mbappe_details = calculate_player_oart(
    mbappe_passes, frames_df, model, feature_cols
)

# ============================================================
# PASO 7: Resultados
# ============================================================

print("\n" + "=" * 60)
print("📊 RESULTADOS OART")
print("=" * 60)

messi_oart = np.mean(messi_oart_scores) if messi_oart_scores else 0
mbappe_oart = np.mean(mbappe_oart_scores) if mbappe_oart_scores else 0

print(f"\n🇦🇷 MESSI:")
print(f"   OART promedio: {messi_oart:.3f}")
print(f"   Pases analizados: {len(messi_oart_scores)}")
print(f"   Desv. estándar: {np.std(messi_oart_scores):.3f}" if messi_oart_scores else "   N/A")

print(f"\n🇫🇷 MBAPPÉ:")
print(f"   OART promedio: {mbappe_oart:.3f}")
print(f"   Pases analizados: {len(mbappe_oart_scores)}")
print(f"   Desv. estándar: {np.std(mbappe_oart_scores):.3f}" if mbappe_oart_scores else "   N/A")

# Interpretación
print("\n" + "=" * 60)
print("🎯 INTERPRETACIÓN")
print("=" * 60)

if messi_oart > mbappe_oart:
    diff = messi_oart - mbappe_oart
    print(f"\n→ Messi es MÁS ARRIESGADO en sus pases (+{diff:.3f})")
    print(f"  Elige opciones más difíciles cuando tiene alternativas fáciles")
else:
    diff = mbappe_oart - messi_oart
    print(f"\n→ Mbappé es MÁS ARRIESGADO en sus pases (+{diff:.3f})")
    print(f"  Elige opciones más difíciles cuando tiene alternativas fáciles")

# Escala de interpretación
print(f"""
📊 Escala de OART:
   0.0 - 0.3: Muy conservador (siempre elige lo seguro)
   0.3 - 0.5: Moderado
   0.5 - 0.7: Arriesgado
   0.7 - 1.0: Muy arriesgado (ignora opciones seguras)
   
   Messi ({messi_oart:.3f}): {"Conservador" if messi_oart < 0.3 else "Moderado" if messi_oart < 0.5 else "Arriesgado" if messi_oart < 0.7 else "Muy arriesgado"}
   Mbappé ({mbappe_oart:.3f}): {"Conservador" if mbappe_oart < 0.3 else "Moderado" if mbappe_oart < 0.5 else "Arriesgado" if mbappe_oart < 0.7 else "Muy arriesgado"}
""")

# Guardar resultados
oart_results = {
    'messi': {
        'oart_mean': float(messi_oart),
        'oart_std': float(np.std(messi_oart_scores)) if messi_oart_scores else 0,
        'passes_analyzed': len(messi_oart_scores),
        'details': messi_details
    },
    'mbappe': {
        'oart_mean': float(mbappe_oart),
        'oart_std': float(np.std(mbappe_oart_scores)) if mbappe_oart_scores else 0,
        'passes_analyzed': len(mbappe_oart_scores),
        'details': mbappe_details
    }
}

# Guardar como JSON
with open('data/oart_results.json', 'w') as f:
    json.dump(oart_results, f, indent=2)

print(f"\n✅ Resultados guardados en: data/oart_results.json")

# ============================================================
# PASO 8: Visualización
# ============================================================

import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Distribución de OART
ax1 = axes[0, 0]
if messi_oart_scores:
    ax1.hist(messi_oart_scores, bins=20, alpha=0.6, label=f'Messi (μ={messi_oart:.3f})', 
             color='#75AADB', edgecolor='black')
if mbappe_oart_scores:
    ax1.hist(mbappe_oart_scores, bins=20, alpha=0.6, label=f'Mbappé (μ={mbappe_oart:.3f})', 
             color='#002654', edgecolor='black')
ax1.axvline(x=0.5, color='red', linestyle='--', label='Neutral (0.5)')
ax1.set_xlabel('OART Score')
ax1.set_ylabel('Frecuencia')
ax1.set_title('Distribución de OART por Pase', fontweight='bold')
ax1.legend()

# 2. Comparación de medias
ax2 = axes[0, 1]
players = ['Messi', 'Mbappé']
oarts = [messi_oart, mbappe_oart]
colors = ['#75AADB', '#002654']
bars = ax2.bar(players, oarts, color=colors, edgecolor='black', linewidth=2)
ax2.axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='Neutral')
ax2.set_ylabel('OART Promedio')
ax2.set_title('OART Promedio por Jugador', fontweight='bold')
ax2.set_ylim(0, 1)
for bar, oart in zip(bars, oarts):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'{oart:.3f}', ha='center', va='bottom', fontsize=14, fontweight='bold')
ax2.legend()

# 3. OART vs Distancia del pase (Messi)
ax3 = axes[1, 0]
if messi_details:
    messi_df = pd.DataFrame(messi_details)
    ax3.scatter(messi_df['pass_distance'], messi_df['oart'], 
               alpha=0.5, color='#75AADB', s=30)
    # Línea de tendencia
    z = np.polyfit(messi_df['pass_distance'], messi_df['oart'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(messi_df['pass_distance'].min(), messi_df['pass_distance'].max(), 100)
    ax3.plot(x_line, p(x_line), "r--", alpha=0.8, label='Tendencia')
ax3.set_xlabel('Distancia del Pase (m)')
ax3.set_ylabel('OART')
ax3.set_title('Messi: OART vs Distancia', fontweight='bold')
ax3.legend()

# 4. OART vs Distancia del pase (Mbappé)
ax4 = axes[1, 1]
if mbappe_details:
    mbappe_df = pd.DataFrame(mbappe_details)
    ax4.scatter(mbappe_df['pass_distance'], mbappe_df['oart'],
               alpha=0.5, color='#002654', s=30)
    # Línea de tendencia
    z = np.polyfit(mbappe_df['pass_distance'], mbappe_df['oart'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(mbappe_df['pass_distance'].min(), mbappe_df['pass_distance'].max(), 100)
    ax4.plot(x_line, p(x_line), "r--", alpha=0.8, label='Tendencia')
ax4.set_xlabel('Distancia del Pase (m)')
ax4.set_ylabel('OART')
ax4.set_title('Mbappé: OART vs Distancia', fontweight='bold')
ax4.legend()

plt.suptitle('Análisis OART - Messi vs Mbappé\nMundial Qatar 2022', 
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('outputs/oart_comparison.png', dpi=150, bbox_inches='tight')
plt.close()

print("✅ Visualización guardada: outputs/oart_comparison.png")