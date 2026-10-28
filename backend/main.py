from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.pc_controller import router as pc_router

app = FastAPI(
    title="Guía Interactiva de Armado de PC - TP Final POO 3 (Grupo 7)",
    description="API Backend en capas para selección y validación de compatibilidad de hardware.",
    version="1.0.0"
)

# Habilitar CORS para permitir peticiones desde el frontend en localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite llamados desde cualquier origen en desarrollo (Live Server, etc.)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],
)

# Registramos el router del controlador
app.include_router(pc_router)

@app.get("/")
def root():
    return {
        "proyecto": "TP Final POO 3 - Grupo 7",
        "estado": "Backend FastAPI en backend/ funcionando",
        "documentacion": "/docs"
    }