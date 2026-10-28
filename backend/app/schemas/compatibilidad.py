"""
Esquemas de validación de Pydantic (DTOs) para la verificación de compatibilidad.

Definen los contratos de datos de entrada y salida para la comunicación 
entre el Frontend y FastAPI.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class SolicitudValidacionSchema(BaseModel):
    """
    DTO de Entrada: Estructura de datos que envía el Frontend mediante POST 
    para solicitar la validación de un armado.
    """
    id_perfil: Optional[int] = Field(
        None, 
        description="ID del perfil de uso elegido por el usuario (ej. Gaming, Oficina)."
    )
    componentes_ids: List[int] = Field(
        ..., 
        description="Lista con los IDs de los componentes seleccionados para el armado."
    )

    class Config:
        # Ejemplo para la documentación interactiva de Swagger UI (/docs)
        json_schema_extra = {
            "example": {
                "id_perfil": 1,
                "componentes_ids": [1, 5, 12, 18, 22]
            }
        }


class RespuestaValidacionSchema(BaseModel):
    """
    DTO de Salida: Estructura de datos que responde FastAPI al Frontend 
    con el resultado de evaluar las reglas de compatibilidad.
    """
    es_compatible: bool = Field(
        ..., 
        description="Indica si la configuración total es compatible de punta a punta."
    )
    advertencias: List[str] = Field(
        default_factory=list, 
        description="Lista de avisos no bloqueantes (ej. potencia ajustada)."
    )
    errores: List[str] = Field(
        default_factory=list, 
        description="Lista de errores bloqueantes (ej. socket de CPU incompatible con la Motherboard)."
    )