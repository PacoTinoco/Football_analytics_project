"""
Football Analytics Platform - Backend Principal
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sys
import os
import uuid
from datetime import datetime

# Añadir el directorio app al path para importar services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Crear app
app = FastAPI(
    title="⚽ Football Analytics Platform",
    description="Plataforma de análisis táctico de fútbol con IA",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorios (rutas relativas desde donde se ejecuta)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

# Crear directorios si no existen
for dir_path in [UPLOAD_DIR, RESULTS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Base de datos en memoria
jobs = {}

# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

@app.get("/")
def home():
    """Redirige a la aplicación."""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/app")
def serve_app():
    """Sirve la aplicación web."""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# ============================================================
# API INFO
# ============================================================

@app.get("/api")
def api_info():
    """Info de la API."""
    return {
        "name": "⚽ Football Analytics Platform",
        "version": "2.0.0",
        "modules": {
            "video": "/api/video",
            "teams": "/api/teams", 
            "players": "/api/players"
        }
    }

# ============================================================
# MÓDULO VIDEO
# ============================================================

@app.post("/api/video/upload")
async def upload_video(file: UploadFile = File(...)):
    """Sube un video para análisis."""
    
    allowed = ['.mp4', '.avi', '.mov', '.mkv']
    ext = os.path.splitext(file.filename)[1].lower()
    
    if ext not in allowed:
        raise HTTPException(400, f"Formato no soportado. Use: {allowed}")
    
    job_id = str(uuid.uuid4())[:8]
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}{ext}")
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    jobs[job_id] = {
        "id": job_id,
        "type": "video",
        "filename": file.filename,
        "filepath": file_path,
        "status": "uploaded",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "results": None
    }
    
    return {"success": True, "job_id": job_id, "message": "Video subido"}


@app.post("/api/video/analyze/{job_id}")
async def analyze_video(job_id: str):
    """Analiza un video con YOLO."""
    
    if job_id not in jobs:
        raise HTTPException(404, "Job no encontrado")
    
    job = jobs[job_id]
    job["status"] = "processing"
    
    try:
        from services.video_analyzer import analyze_video_full
        results = analyze_video_full(job["filepath"], job_id)
        
        job["status"] = "completed"
        job["progress"] = 100
        job["results"] = results
        
        return {"success": True, "job_id": job_id, "results": results}
        
    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
        raise HTTPException(500, str(e))


# ============================================================
# MÓDULO EQUIPOS
# ============================================================

@app.get("/api/teams/available")
def get_available_teams():
    """Lista equipos disponibles."""
    return {
        "worldcup_2022": ["Argentina", "France", "Croatia", "Morocco", 
                         "Netherlands", "England", "Brazil", "Portugal"]
    }


@app.get("/api/teams/compare")
async def compare_teams(team1: str, team2: str, competition: str = "worldcup_2022"):
    """Compara dos equipos."""
    
    try:
        from services.team_analyzer import compare_teams_style
        results = compare_teams_style(team1, team2, competition)
        return {"success": True, "comparison": results}
        
    except Exception as e:
        raise HTTPException(500, str(e))


# ============================================================
# MÓDULO JUGADORES
# ============================================================

@app.get("/api/players/available")
def get_available_players():
    """Lista jugadores disponibles."""
    return {
        "argentina": ["Messi", "Di María", "Álvarez", "Enzo Fernández"],
        "france": ["Mbappé", "Griezmann", "Giroud", "Tchouaméni"]
    }


@app.get("/api/players/compare")
async def compare_players(player1: str, player2: str):
    """Compara dos jugadores."""
    
    try:
        from services.player_analyzer import compare_two_players
        results = compare_two_players(player1, player2)
        return {"success": True, "comparison": results}
        
    except Exception as e:
        raise HTTPException(500, str(e))


# ============================================================
# UTILIDADES
# ============================================================

@app.get("/api/jobs")
def list_jobs():
    """Lista todos los trabajos."""
    return {"total": len(jobs), "jobs": list(jobs.values())}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    """Obtiene estado de un trabajo."""
    if job_id not in jobs:
        raise HTTPException(404, "Job no encontrado")
    return jobs[job_id]


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)