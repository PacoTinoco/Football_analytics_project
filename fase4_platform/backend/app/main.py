"""
Football Analytics API - Backend principal
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import shutil
import os
import uuid
from datetime import datetime

# Crear app
app = FastAPI(
    title="Football Analytics API",
    description="API para análisis de video de fútbol con IA",
    version="1.0.0"
)

# Configurar CORS para permitir requests del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorios
UPLOAD_DIR = "uploads"
RESULTS_DIR = "results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Base de datos simple (en memoria)
jobs = {}


@app.get("/")
def root():
    """Endpoint de bienvenida."""
    return {
        "message": "🎉 Football Analytics API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/upload",
            "status": "/api/status/{job_id}",
            "results": "/api/results/{job_id}"
        }
    }


@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Sube un video para análisis.
    Retorna un job_id para consultar el estado.
    """
    # Validar extensión
    allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    ext = os.path.splitext(file.filename)[1].lower()
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado. Use: {allowed_extensions}"
        )
    
    # Generar ID único
    job_id = str(uuid.uuid4())[:8]
    
    # Guardar archivo
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}{ext}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Registrar job
    jobs[job_id] = {
        "id": job_id,
        "filename": file.filename,
        "filepath": file_path,
        "status": "uploaded",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "results": None
    }
    
    return {
        "success": True,
        "job_id": job_id,
        "message": f"Video '{file.filename}' subido correctamente",
        "next_step": f"POST /api/analyze/{job_id} para iniciar análisis"
    }


@app.post("/api/analyze/{job_id}")
async def analyze_video(job_id: str):
    """
    Inicia el análisis de un video subido.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    
    job = jobs[job_id]
    
    if job["status"] == "processing":
        return {"message": "El análisis ya está en proceso"}
    
    # Actualizar estado
    job["status"] = "processing"
    job["progress"] = 0
    
    # Procesar video (simplificado - en producción usar background task)
    try:
        from processing.analyzer import analyze_football_video
        
        results = analyze_football_video(
            video_path=job["filepath"],
            job_id=job_id,
            progress_callback=lambda p: update_progress(job_id, p)
        )
        
        job["status"] = "completed"
        job["progress"] = 100
        job["results"] = results
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Análisis completado",
            "results_url": f"/api/results/{job_id}"
        }
        
    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))


def update_progress(job_id: str, progress: int):
    """Actualiza el progreso de un job."""
    if job_id in jobs:
        jobs[job_id]["progress"] = progress


@app.get("/api/status/{job_id}")
def get_status(job_id: str):
    """
    Obtiene el estado de un job de análisis.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    
    job = jobs[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "filename": job["filename"],
        "created_at": job["created_at"]
    }


@app.get("/api/results/{job_id}")
def get_results(job_id: str):
    """
    Obtiene los resultados del análisis.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    
    job = jobs[job_id]
    
    if job["status"] != "completed":
        return {
            "job_id": job_id,
            "status": job["status"],
            "message": "El análisis aún no ha terminado"
        }
    
    return {
        "job_id": job_id,
        "status": "completed",
        "results": job["results"]
    }


@app.get("/api/jobs")
def list_jobs():
    """Lista todos los jobs."""
    return {
        "total": len(jobs),
        "jobs": [
            {
                "id": j["id"],
                "filename": j["filename"],
                "status": j["status"],
                "progress": j["progress"]
            }
            for j in jobs.values()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)