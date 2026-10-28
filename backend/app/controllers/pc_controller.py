import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.domain.modelos import Componente, ConfiguracionPC, Marca, TipoComponente, Usuario
from app.domain.reglas import ReglaConsumoFuenteStrategy, ReglaSocketCpuMotherboardStrategy
from app.repositories import ComponenteRepository, PerfilRepository
from app.schemas.compatibilidad import RespuestaValidacionSchema, SolicitudValidacionSchema
from app.services.compatibilidad_service import ValidadorCompatibilidadService

router = APIRouter(prefix="/api/v1", tags=["Configuraciones y Compatibilidad"])

componente_repo = ComponenteRepository()
perfil_repo = PerfilRepository()


@router.post("/compatibilidad/validar", response_model=RespuestaValidacionSchema)
def validar_compatibilidad_hu1(solicitud: SolicitudValidacionSchema):
    try:
        if not solicitud.componentes_ids:
            return RespuestaValidacionSchema(
                es_compatible=False,
                advertencias=[],
                errores=["No se han seleccionado componentes para validar."]
            )

        usuario_temp = Usuario(
            id_usuario=1,
            nombre="Estudiante",
            apellido="POO3",
            email="user@mail.com",
            password_hash="xxx"
        )
        config_pc = ConfiguracionPC(
            id_configuracion=100,
            usuario=usuario_temp,
            nombre="Armado HU-1"
        )

        componentes_no_encontrados = []

        for comp_id in solicitud.componentes_ids:
            try:
                datos_comp = componente_repo.obtener_por_id(comp_id)
            except Exception:
                datos_comp = None

            if datos_comp:
                if isinstance(datos_comp, str):
                    try:
                        datos_comp = json.loads(datos_comp)
                    except json.JSONDecodeError:
                        datos_comp = None

                if isinstance(datos_comp, dict):
                    specs = datos_comp.get("especificaciones", {})
                    if isinstance(specs, str):
                        try:
                            specs = json.loads(specs)
                        except json.JSONDecodeError:
                            specs = {}

                    categoria_val = datos_comp.get("categoria") or datos_comp.get("tipo") or "General"
                    nombre_tipo = categoria_val.get("nombre", "General") if isinstance(categoria_val, dict) else str(categoria_val)

                    tipo_obj = TipoComponente(
                        id_tipo=datos_comp.get("id_tipo", 1),
                        nombre=nombre_tipo,
                        obligatorio=False
                    )

                    marca_val = datos_comp.get("marca", "Genérica")
                    nombre_marca = marca_val.get("nombre", "Genérica") if isinstance(marca_val, dict) else str(marca_val)

                    marca_obj = Marca(
                        id_marca=datos_comp.get("id_marca", 1),
                        nombre=nombre_marca
                    )

                    componente_dominio = Componente(
                        id_componente=datos_comp.get("id_componente", comp_id),
                        tipo=tipo_obj,
                        marca=marca_obj,
                        nombre=datos_comp.get("nombre", f"Componente {comp_id}"),
                        modelo=datos_comp.get("modelo"),
                        descripcion=datos_comp.get("descripcion"),
                        consumo_watts=datos_comp.get("consumo_watts", 0),
                        precio_referencia=datos_comp.get("precio_referencia", 0.0),
                        stock=datos_comp.get("stock", 0),
                        especificaciones=specs
                    )
                    config_pc.agregar_componente(componente_dominio)

                elif hasattr(datos_comp, "id_componente"):
                    config_pc.agregar_componente(datos_comp)
                else:
                    componentes_no_encontrados.append(comp_id)
            else:
                componentes_no_encontrados.append(comp_id)

        if componentes_no_encontrados:
            return RespuestaValidacionSchema(
                es_compatible=False,
                advertencias=[],
                errores=[f"No se encontraron componentes con ID: {componentes_no_encontrados}"]
            )

        # Reglas del Dominio
        regla_fuente = ReglaConsumoFuenteStrategy(
            id_regla=1, nombre="Capacidad de Fuente", descripcion="Valida watts", codigo="VAL_WATTS", nivel="ERROR"
        )
        regla_socket = ReglaSocketCpuMotherboardStrategy(
            id_regla=2, nombre="Compatibilidad de Socket", descripcion="Valida sockets", codigo="VAL_SOCKET", nivel="ERROR"
        )

        servicio = ValidadorCompatibilidadService(reglas=[regla_fuente, regla_socket])
        resultados = servicio.validar_configuracion(config_pc)

        # PROCESAMIENTO CORRECTO DEL DICCIONARIO O LISTA DE RESULTADOS
        errores = []
        advertencias = []

        if isinstance(resultados, dict):
            # Si el servicio devuelve la estructura de objeto
            lista_incompat = resultados.get("incompatibilidades") or resultados.get("detalles") or []
            if isinstance(lista_incompat, list):
                for item in lista_incompat:
                    if isinstance(item, dict):
                        msg = item.get("mensaje") or item.get("descripcion") or str(item)
                    else:
                        msg = str(item)
                    errores.append(msg)
            elif not resultados.get("es_compatible", True):
                errores.append("Incompatibilidad detectada en la configuración.")
        elif isinstance(resultados, list):
            for r in resultados:
                if isinstance(r, dict):
                    msg = r.get("mensaje") or r.get("descripcion") or str(r)
                    est = r.get("estado") or r.get("nivel") or "ERROR"
                else:
                    msg = getattr(r, "mensaje", str(r))
                    est = getattr(r, "estado", "ERROR")

                if est in ["ERROR", "CRITICO"]:
                    errores.append(msg)
                else:
                    advertencias.append(msg)

        es_comp = resultados.get("es_compatible", len(errores) == 0) if isinstance(resultados, dict) else (len(errores) == 0)

        return RespuestaValidacionSchema(
            es_compatible=es_comp,
            advertencias=advertencias,
            errores=errores
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en validación: {str(e)}")


@router.get("/perfiles")
def listar_perfiles():
    return perfil_repo.obtener_todos()


@router.get("/componentes")
def listar_componentes(id_tipo: Optional[int] = None):
    if id_tipo:
        return componente_repo.obtener_por_categoria(id_tipo)
    return componente_repo.obtener_todos()