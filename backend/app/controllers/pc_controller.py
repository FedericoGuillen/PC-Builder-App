from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Importamos nuestro Dominio y Servicios
from app.domain.modelos import Usuario, Marca, TipoComponente, Componente, ConfiguracionPC
from app.domain.reglas import ReglaConsumoFuenteStrategy, ReglaSocketCpuMotherboardStrategy
from app.services.compatibilidad_service import ValidadorCompatibilidadService

router = APIRouter(prefix="/api/v1", tags=["Configuraciones y Compatibilidad"])

# --- Esquemas Pydantic para validar los datos que entran por HTTP ---
class ItemComponenteSchema(BaseModel):
    id_componente: int
    nombre: str
    tipo: str  # Ej: "Procesador", "Placa Madre", "Fuente de Poder", "Placa de Video"
    consumo_watts: int
    precio: float
    especificaciones: dict  # Recibe el JSONB de especificaciones (ej: {"watts": 650, "socket": "AM5"})

class ValidarPCRequestSchema(BaseModel):
    nombre_configuracion: str
    componentes: List[ItemComponenteSchema]

@router.post("/pc/validar-compatibilidad")
def validar_compatibilidad_pc(data: ValidarPCRequestSchema):
    """
    Endpoint que recibe una lista de componentes de una PC en armado,
    construye los objetos del Dominio al vuelo y evalúa las reglas de compatibilidad.
    """
    try:
        # 1. Creamos un usuario ficticio temporal para el contexto de la prueba de API
        usuario_temp = Usuario(id_usuario=1, nombre="Estudiante", apellido="POO3", email="user@mail.com", password_hash="xxx")
        
        # 2. Creamos la Configuración de PC en el Dominio
        config_pc = ConfiguracionPC(id_configuracion=100, usuario=usuario_temp, nombre=data.nombre_configuracion)
        
        # 3. Mapeamos los datos que vinieron por JSON hacia nuestras clases del Dominio
        for item in data.componentes:
            # Creamos instancias simplificadas de Marca y TipoComponente para el mapeo
            marca_mock = Marca(id_marca=1, nombre="Genérica")
            tipo_mock = TipoComponente(id_tipo=1, nombre=item.tipo, obligatorio=False)
            
            componente_dominio = Componente(
                id_componente=item.id_componente,
                tipo=tipo_mock,
                marca=marca_mock,
                nombre=item.nombre,
                modelo=None,
                descripcion=None,
                consumo_watts=item.consumo_watts,
                precio_referencia=item.precio,
                stock=10,
                especificaciones=item.especificaciones
            )
            
            config_pc.agregar_componente(componente_dominio)

        # 4. Instanciamos las reglas del negocio
        regla_fuente = ReglaConsumoFuenteStrategy(
            id_regla=1, nombre="Capacidad de Fuente", descripcion="Valida watts", codigo="VAL_WATTS", nivel="ERROR"
        )
        regla_socket = ReglaSocketCpuMotherboardStrategy(
            id_regla=2, nombre="Compatibilidad de Socket", descripcion="Valida sockets", codigo="VAL_SOCKET", nivel="ERROR"
        )
        
        # 5. Inyectamos las reglas al Servicio de Validación
        servicio = ValidadorCompatibilidadService(reglas=[regla_fuente, regla_socket])
        
        # 6. Ejecutamos la lógica de negocio pura
        resultados = servicio.validar_configuracion(config_pc)
        
        # 7. Retornamos la respuesta consolidada en formato JSON
        return {
            "configuracion": data.nombre_configuracion,
            "precio_total": config_pc.precio_total,
            "consumo_total_watts": config_pc.consumo_total_watts,
            "resultados_compatibilidad": resultados
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))