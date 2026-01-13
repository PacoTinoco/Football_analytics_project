// ============================================
// FOOTBALL ANALYTICS PLATFORM - APP.JS
// ============================================

const API_URL = 'http://localhost:8000';

// ============================================
// NAVIGATION
// ============================================

function showSection(sectionId) {
    // Ocultar todas las secciones
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Mostrar la sección seleccionada
    document.getElementById(sectionId).classList.add('active');
    
    // Actualizar navegación
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.classList.remove('active');
    });
    event.target.classList.add('active');
}

// ============================================
// VIDEO ANALYSIS
// ============================================

// Drag and drop
const uploadArea = document.getElementById('uploadArea');
const videoInput = document.getElementById('videoInput');

if (uploadArea) {
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file) handleVideoUpload(file);
    });
}

if (videoInput) {
    videoInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleVideoUpload(file);
    });
}

async function handleVideoUpload(file) {
    const progressContainer = document.getElementById('videoProgress');
    const progressBar = document.getElementById('videoProgressBar');
    const statusText = document.getElementById('videoStatus');
    const resultsContainer = document.getElementById('videoResults');
    
    progressContainer.style.display = 'block';
    resultsContainer.style.display = 'none';
    
    try {
        // Upload
        statusText.textContent = 'Subiendo video...';
        progressBar.style.width = '20%';
        
        const formData = new FormData();
        formData.append('file', file);
        
        const uploadRes = await fetch(`${API_URL}/api/video/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!uploadRes.ok) throw new Error('Error al subir');
        
        const uploadData = await uploadRes.json();
        const jobId = uploadData.job_id;
        
        // Analyze
        statusText.textContent = 'Analizando con YOLO...';
        progressBar.style.width = '50%';
        
        const analyzeRes = await fetch(`${API_URL}/api/video/analyze/${jobId}`, {
            method: 'POST'
        });
        
        if (!analyzeRes.ok) throw new Error('Error al analizar');
        
        const analyzeData = await analyzeRes.json();
        
        progressBar.style.width = '100%';
        statusText.textContent = '¡Completado!';
        
        // Show results
        displayVideoResults(analyzeData.results);
        
    } catch (error) {
        statusText.textContent = `Error: ${error.message}`;
        progressBar.style.width = '0%';
    }
}

function displayVideoResults(results) {
    const container = document.getElementById('videoResults');
    container.style.display = 'block';
    
    container.innerHTML = `
        <h3>📊 Resultados del Análisis</h3>
        
        <div class="results-grid">
            <div class="result-card">
                <div class="label">Duración</div>
                <div class="value">${results.video_info.duration_sec}s</div>
            </div>
            <div class="result-card">
                <div class="label">FPS</div>
                <div class="value">${results.video_info.fps}</div>
            </div>
            <div class="result-card">
                <div class="label">Detecciones</div>
                <div class="value">${results.detection_summary.total_detections}</div>
            </div>
            <div class="result-card">
                <div class="label">Jugadores Únicos</div>
                <div class="value">${results.detection_summary.unique_players}</div>
            </div>
        </div>
        
        <h4>🏃 Top Jugadores por Actividad</h4>
        <table class="comparison-table">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>ID</th>
                    <th>Frames</th>
                    <th>Distancia (px)</th>
                </tr>
            </thead>
            <tbody>
                ${results.player_metrics.map((p, i) => `
                    <tr>
                        <td>${i + 1}</td>
                        <td>#${p.tracker_id}</td>
                        <td>${p.frames_tracked}</td>
                        <td>${p.distance_px}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ============================================
// TEAM ANALYSIS
// ============================================

async function compareTeams() {
    const team1 = document.getElementById('team1Select').value;
    const team2 = document.getElementById('team2Select').value;
    const resultsContainer = document.getElementById('teamsResults');
    
    if (!team1 || !team2) {
        alert('Por favor selecciona ambos equipos');
        return;
    }
    
    resultsContainer.style.display = 'block';
    resultsContainer.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <span>Analizando equipos...</span>
        </div>
    `;
    
    try {
        const res = await fetch(`${API_URL}/api/teams/compare?team1=${team1}&team2=${team2}`);
        
        if (!res.ok) throw new Error('Error al comparar equipos');
        
        const data = await res.json();
        displayTeamComparison(data.comparison);
        
    } catch (error) {
        resultsContainer.innerHTML = `
            <div class="error-message">Error: ${error.message}</div>
        `;
    }
}

function displayTeamComparison(data) {
    const container = document.getElementById('teamsResults');
    const t1 = data.team1;
    const t2 = data.team2;
    
    container.innerHTML = `
        <h3>📊 Comparación de Equipos</h3>
        
        <div class="results-grid">
            <div class="result-card">
                <div class="label">${t1.team} - Goles</div>
                <div class="value">${t1.goals}</div>
            </div>
            <div class="result-card">
                <div class="label">${t2.team} - Goles</div>
                <div class="value">${t2.goals}</div>
            </div>
            <div class="result-card">
                <div class="label">${t1.team} - xG</div>
                <div class="value">${t1.xg}</div>
            </div>
            <div class="result-card">
                <div class="label">${t2.team} - xG</div>
                <div class="value">${t2.xg}</div>
            </div>
        </div>
        
        <table class="comparison-table">
            <thead>
                <tr>
                    <th>Métrica</th>
                    <th>${t1.team}</th>
                    <th>${t2.team}</th>
                    <th>Ventaja</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Goles</td>
                    <td>${t1.goals}</td>
                    <td>${t2.goals}</td>
                    <td class="winner">${data.comparison.more_goals}</td>
                </tr>
                <tr>
                    <td>xG</td>
                    <td>${t1.xg}</td>
                    <td>${t2.xg}</td>
                    <td class="winner">${t1.xg > t2.xg ? t1.team : t2.team}</td>
                </tr>
                <tr>
                    <td>Precisión Pase</td>
                    <td>${t1.pass_accuracy}%</td>
                    <td>${t2.pass_accuracy}%</td>
                    <td class="winner">${data.comparison.better_passing}</td>
                </tr>
                <tr>
                    <td>Pressing/Partido</td>
                    <td>${t1.pressures_per_game}</td>
                    <td>${t2.pressures_per_game}</td>
                    <td class="winner">${data.comparison.more_pressing}</td>
                </tr>
                <tr>
                    <td>Conversión</td>
                    <td>${t1.conversion_rate}%</td>
                    <td>${t2.conversion_rate}%</td>
                    <td class="winner">${data.comparison.more_efficient}</td>
                </tr>
                <tr>
                    <td>Éxito Regates</td>
                    <td>${t1.dribble_success}%</td>
                    <td>${t2.dribble_success}%</td>
                    <td class="winner">${t1.dribble_success > t2.dribble_success ? t1.team : t2.team}</td>
                </tr>
            </tbody>
        </table>
    `;
}

// ============================================
// PLAYER ANALYSIS
// ============================================

async function comparePlayers() {
    const player1 = document.getElementById('player1Select').value;
    const player2 = document.getElementById('player2Select').value;
    const resultsContainer = document.getElementById('playersResults');
    
    if (!player1 || !player2) {
        alert('Por favor selecciona ambos jugadores');
        return;
    }
    
    resultsContainer.style.display = 'block';
    resultsContainer.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <span>Analizando jugadores...</span>
        </div>
    `;
    
    try {
        const res = await fetch(`${API_URL}/api/players/compare?player1=${player1}&player2=${player2}`);
        
        if (!res.ok) throw new Error('Error al comparar jugadores');
        
        const data = await res.json();
        displayPlayerComparison(data.comparison);
        
    } catch (error) {
        resultsContainer.innerHTML = `
            <div class="error-message">Error: ${error.message}</div>
        `;
    }
}

function displayPlayerComparison(data) {
    const container = document.getElementById('playersResults');
    const p1 = data.player1;
    const p2 = data.player2;
    
    container.innerHTML = `
        <h3>👥 Comparación de Jugadores</h3>
        
        <div class="results-grid">
            <div class="result-card">
                <div class="label">${p1.player} - G+A</div>
                <div class="value">${p1.goals + p1.assists}</div>
            </div>
            <div class="result-card">
                <div class="label">${p2.player} - G+A</div>
                <div class="value">${p2.goals + p2.assists}</div>
            </div>
            <div class="result-card">
                <div class="label">${p1.player} - xG</div>
                <div class="value">${p1.xg}</div>
            </div>
            <div class="result-card">
                <div class="label">${p2.player} - xG</div>
                <div class="value">${p2.xg}</div>
            </div>
        </div>
        
        <table class="comparison-table">
            <thead>
                <tr>
                    <th>Métrica</th>
                    <th>${p1.player}</th>
                    <th>${p2.player}</th>
                    <th>Ventaja</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Goles</td>
                    <td>${p1.goals}</td>
                    <td>${p2.goals}</td>
                    <td class="winner">${data.comparison.more_goals}</td>
                </tr>
                <tr>
                    <td>Asistencias</td>
                    <td>${p1.assists}</td>
                    <td>${p2.assists}</td>
                    <td class="winner">${data.comparison.more_assists}</td>
                </tr>
                <tr>
                    <td>xG</td>
                    <td>${p1.xg}</td>
                    <td>${p2.xg}</td>
                    <td class="winner">${p1.xg > p2.xg ? p1.player : p2.player}</td>
                </tr>
                <tr>
                    <td>Sobre xG</td>
                    <td>${p1.goals_over_xg > 0 ? '+' : ''}${p1.goals_over_xg}</td>
                    <td>${p2.goals_over_xg > 0 ? '+' : ''}${p2.goals_over_xg}</td>
                    <td class="winner">${data.comparison.better_conversion}</td>
                </tr>
                <tr>
                    <td>Pases Clave</td>
                    <td>${p1.key_passes}</td>
                    <td>${p2.key_passes}</td>
                    <td class="winner">${data.comparison.more_creative}</td>
                </tr>
                <tr>
                    <td>Precisión Pase</td>
                    <td>${p1.pass_accuracy}%</td>
                    <td>${p2.pass_accuracy}%</td>
                    <td class="winner">${p1.pass_accuracy > p2.pass_accuracy ? p1.player : p2.player}</td>
                </tr>
                <tr>
                    <td>Regates Exitosos</td>
                    <td>${p1.dribbles_successful}/${p1.dribbles_attempted}</td>
                    <td>${p2.dribbles_successful}/${p2.dribbles_attempted}</td>
                    <td class="winner">${data.comparison.better_dribbler}</td>
                </tr>
                <tr>
                    <td>% Regates</td>
                    <td>${p1.dribble_success_rate}%</td>
                    <td>${p2.dribble_success_rate}%</td>
                    <td class="winner">${data.comparison.better_dribbler}</td>
                </tr>
            </tbody>
        </table>
    `;
}

// ============================================
// INIT
// ============================================

console.log('⚽ Football Analytics Platform loaded');