from typing import List, Dict, Any
from app.domain.modelos import ConfiguracionPC
from app.domain.reglas import (
    ReglaCompatibilidadStrategy,
    ReglaConsumoFuenteStrategy,
    ReglaSocketCpuMotherboardStrategy,
    ReglaRamMotherboardStrategy,
    ReglaGabineteMotherboardStrategy
)

class ValidadorCompatibilidadService:
    """
    Servicio de aplicación encargado de orquestar la validación de compatibilidad 
    sobre una configuración de PC utilizando el conjunto de reglas disponibles (Patrón Strategy).
    """
    def __init__(self, reglas: List[ReglaCompatibilidadStrategy] = None):
        if reglas is None:
            # Carga por defecto las 4 reglas del sistema
            self.reglas = [
                ReglaConsumoFuenteStrategy(),
                ReglaSocketCpuMotherboardStrategy(),
                ReglaRamMotherboardStrategy(),
                ReglaGabineteMotherboardStrategy()
            ]
        else:
            self.reglas = reglas

    def validar_configuracion(self, configuracion: ConfiguracionPC) -> Dict[str, Any]:
        """
        Ejecuta todas las reglas configuradas sobre la PC.
        Devuelve el estado general y la lista explicativa de incompatibilidades.
        """
        incompatibilidades: List[str] = []
        detalles: List[Dict[str, Any]] = []

        for regla in self.reglas:
            if not regla.activa:
                continue

            resultado = regla.evaluar(configuracion)

            if resultado:
                mensaje = resultado.get("mensaje", "")
                incompatibilidades.append(mensaje)
                
                detalles.append({
                    "id_regla": regla.id_regla,
                    "codigo_regla": regla.codigo,
                    "nombre_regla": regla.nombre,
                    "nivel": regla.nivel,
                    "resultado": resultado.get("resultado", "INCOMPATIBLE"),
                    "mensaje": mensaje
                })

        es_compatible = len(incompatibilidades) == 0

        return {
            "es_compatible": es_compatible,
            "incompatibilidades": incompatibilidades,
            "detalles": detalles
        }