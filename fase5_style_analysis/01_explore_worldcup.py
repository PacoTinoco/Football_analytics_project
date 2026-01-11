"""
Explorar datos disponibles del Real Madrid en StatsBomb.
"""

from statsbombpy import sb
"""
Explorar datos del Mundial 2022 - Argentina y Francia
"""

from statsbombpy import sb
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

print("=" * 60)
print("🏆 MUNDIAL 2022 - ARGENTINA Y FRANCIA")
print("=" * 60)

# Cargar partidos del Mundial 2022
matches = sb.matches(competition_id=43, season_id=106)

print(f"\n📊 Total de partidos en el Mundial: {len(matches)}")

# Filtrar partidos de Argentina
argentina_matches = matches[
    (matches['home_team'] == 'Argentina') | 
    (matches['away_team'] == 'Argentina')
]

# Filtrar partidos de Francia
france_matches = matches[
    (matches['home_team'] == 'France') | 
    (matches['away_team'] == 'France')
]

print(f"\n🇦🇷 Partidos de Argentina: {len(argentina_matches)}")
print("-" * 50)
for _, match in argentina_matches.iterrows():
    result = f"{match['home_team']} {match['home_score']} - {match['away_score']} {match['away_team']}"
    print(f"   {match['match_date']}: {result}")

print(f"\n🇫🇷 Partidos de Francia: {len(france_matches)}")
print("-" * 50)
for _, match in france_matches.iterrows():
    result = f"{match['home_team']} {match['home_score']} - {match['away_score']} {match['away_team']}"
    print(f"   {match['match_date']}: {result}")

# Guardar IDs de partidos para uso posterior
argentina_ids = argentina_matches['match_id'].tolist()
france_ids = france_matches['match_id'].tolist()

# Partidos en común (la final)
common = set(argentina_ids) & set(france_ids)
print(f"\n⭐ Partido en común (Final): {len(common)} partido(s)")

# Guardar info
data = {
    'argentina_match_ids': argentina_ids,
    'france_match_ids': france_ids,
    'total_argentina': len(argentina_matches),
    'total_france': len(france_matches)
}

import json
with open('data/worldcup_matches.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n✅ Datos guardados en: data/worldcup_matches.json")

# Cargar eventos de un partido de ejemplo (la final)
final_id = list(common)[0]
print(f"\n🏆 Cargando eventos de la final (match_id: {final_id})...")

events = sb.events(match_id=final_id)
print(f"   Total eventos: {len(events)}")

# Resumen por equipo
print(f"\n📊 Eventos por equipo en la final:")
print(events['team'].value_counts().to_string())

# Tipos de eventos
print(f"\n📊 Tipos de eventos más comunes:")
print(events['type'].value_counts().head(10).to_string())