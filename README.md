# ⚽ Football Analytics Project: OART Implementation

## Análisis de Riesgo en Pases - FIFA World Cup 2022

Este proyecto implementa una versión del **Opportunity-Adjusted Risk Taking (OART)**, una métrica innovadora para cuantificar las preferencias de riesgo en la selección de pases en fútbol.

Basado en el paper: *"Quantifying Opportunity-Adjusted Risk Taking in Football Pass Selection"* por Lucas Carrasquilla Parra (Universidad del Rosario, 2026).

---

## 🎯 Objetivos del Proyecto

1. **Cargar y explorar** datos StatsBomb del Mundial 2022
2. **Implementar** modelo de predicción de éxito de pases (XGBoost)
3. **Calcular** la métrica OART para evaluar riesgo en decisiones de pase
4. **Visualizar** patrones de riesgo por jugador y equipo
5. **Validar** la métrica con análisis estadístico

---

## 📁 Estructura del Proyecto

```
football_analytics_project/
│
├── README.md                    # Este archivo
├── requirements.txt             # Dependencias Python
├── setup.py                     # Instalación del paquete
│
├── notebooks/
│   ├── 01_data_exploration.ipynb       # Exploración inicial de datos
│   ├── 02_pass_success_model.ipynb     # Modelo de predicción de pases
│   ├── 03_oart_calculation.ipynb       # Cálculo de OART
│   └── 04_visualization_analysis.ipynb # Visualizaciones y análisis
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py          # Funciones para cargar datos StatsBomb
│   ├── feature_engineering.py  # Extracción de características
│   ├── pass_model.py           # Modelo de éxito de pases
│   ├── oart.py                 # Cálculo de OART
│   └── visualization.py        # Funciones de visualización
│
├── data/                        # Datos descargados (no incluido en git)
│   ├── raw/
│   └── processed/
│
├── outputs/                     # Resultados y figuras
│   ├── figures/
│   └── reports/
│
└── docs/                        # Documentación adicional
    └── methodology.md
```

---

## 🚀 Instalación Rápida

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/football-analytics-oart.git
cd football-analytics-oart
```

### 2. Crear entorno virtual
```bash
# Con conda (recomendado)
conda create -n football-analytics python=3.10
conda activate football-analytics

# O con venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar notebooks
```bash
jupyter notebook notebooks/
```

---

## 📊 Datos Utilizados

### StatsBomb Open Data - FIFA World Cup 2022
- **Competition ID:** 43
- **Season ID:** 106
- **Partidos:** 64
- **Eventos de pase:** ~68,000
- **Datos 360°:** Posiciones de todos los jugadores en cada evento

Los datos se descargan automáticamente usando la librería `statsbombpy`.

---

## 🧠 Metodología

### 1. Modelo de Éxito de Pases

Entrenamos un modelo XGBoost para predecir la probabilidad de éxito de un pase basándose en:

**Features Espaciales:**
- Distancia del pase
- Ángulo del pase
- Posición en el campo (x, y)

**Features Tácticas:**
- Presión defensiva
- Número de oponentes en el corredor del pase
- Tamaño del option set (compañeros disponibles)

**Features Contextuales:**
- Minuto del partido
- Diferencia de goles
- Tipo de jugada (juego abierto, set piece, etc.)

### 2. Cálculo de OART

Para cada evento de pase i con conjunto de opciones Aᵢ y receptor elegido cᵢ:

```
OART_i = (1 / |A_i - 1|) × Σ [P(success_j) > P(success_c)]
```

Donde:
- `P(success_j)` = Probabilidad predicha de éxito para pasar al compañero j
- `P(success_c)` = Probabilidad predicha para el receptor elegido
- El resultado está acotado entre 0 y 1

**Interpretación:**
- OART = 0: El jugador eligió la opción con mayor probabilidad de éxito
- OART = 1: Todas las alternativas tenían mayor probabilidad de éxito
- OART alto = Mayor toma de riesgo

---

## 📈 Resultados Esperados

### Métricas del Modelo
- **AUC:** ~0.88
- **Brier Score:** ~0.09

### Validación de OART
- **Split-half reliability:** r ≈ 0.55-0.60
- **Correlación con completion rate:** r ≈ -0.73 (esperado para métrica de riesgo)

---

## 🎨 Visualizaciones Incluidas

1. **Pass Maps** - Distribución espacial de pases por jugador
2. **OART Distribution** - Histogramas a nivel evento y jugador
3. **Risk Profiles** - Comparación de jugadores por OART
4. **Calibration Curves** - Validación del modelo de pases
5. **Feature Importance** - Importancia de características

---

## 📚 Referencias

- Carrasquilla Parra, L. (2026). *Quantifying Opportunity-Adjusted Risk Taking in Football Pass Selection*. Universidad del Rosario.
- StatsBomb Open Data: https://github.com/statsbomb/open-data
- Goes et al. (2022). *Expected passes: Determining the difficulty of a pass in football using spatio-temporal data*.
- Fernández et al. (2021). *A framework for the fine-grained evaluation of the instantaneous expected value of soccer possessions*.

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-metrica`)
3. Commit tus cambios (`git commit -am 'Añadir nueva métrica'`)
4. Push a la rama (`git push origin feature/nueva-metrica`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Los datos de StatsBomb están sujetos a sus propios términos de uso.

---

## 👤 Autor

**Tu Nombre**
- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- LinkedIn: [tu-perfil](https://linkedin.com/in/tu-perfil)
- Twitter: [@tu-handle](https://twitter.com/tu-handle)

---

*Última actualización: Enero 2026*
