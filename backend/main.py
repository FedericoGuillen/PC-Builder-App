from fastapi import FastAPI
from app.controllers.pc_controller import router as pc_router

app = FastAPI(
    title="Guía Interactiva de Armado de PC - TP Final POO 3 (Grupo 7)",
    description="API Backend en capas para selección y validación de compatibilidad de hardware.",
    version="1.0.0"
)

# Registramos el router del controlador de compatibilidad
app.include_router(pc_router)

@app.get("/")
def root():
    return {
        "proyecto": "TP Final POO 3 - Grupo 7",
        "estado": "Backend FastAPI en backend/ funcionando",
        "documentacion": "/docs"
    }