from typing import List, Dict, Any
from app.domain.modelos import ConfiguracionPC
from app.domain.reglas import ReglaCompatibilidadStrategy

class ValidadorCompatibilidadService:
    """
    Servicio de aplicación encargado de orquestar la validación de compatibilidad 
    sobre una configuración de PC utilizando el conjunto de reglas disponibles.
    """
    def __init__(self, reglas: List[ReglaCompatibilidadStrategy]):
        # Inyección de dependencias: recibe la lista de reglas a evaluar
        self.reglas = reglas

    def validar_configuracion(self, configuracion: ConfiguracionPC) -> List[Dict[str, Any]]:
        """
        Ejecuta todas las reglas configuradas sobre la PC y recopila los resultados o advertencias.
        """
        resultados_validacion = []

        for regla in self.reglas:
            if not regla.activa:
                continue  # Si la regla está desactivada en el sistema, la saltamos
                
            # Evaluamos la regla con la lógica del dominio (Patrón Strategy)
            resultado = regla.evaluar(configuracion)
            
            if resultado:
                # Si la regla devuelve un dict, significa que encontró un conflicto o advertencia
                resultado_con_metadatos = {
                    "id_regla": regla.id_regla,
                    "codigo_regla": regla.codigo,
                    "nombre_regla": regla.nombre,
                    "nivel": regla.nivel,
                    "resultado": resultado.get("resultado", "INCOMPATIBLE"),
                    "mensaje": resultado.get("mensaje")
                }
                resultados_validacion.append(resultado_con_metadatos)

        # Si no hubo ningún error/advertencia, podemos devolver un estado global compatible
        if not resultados_validacion:
            resultados_validacion.append({
                "id_regla": 0,
                "codigo_regla": "GENERAL_OK",
                "nombre_regla": "Compatibilidad General",
                "nivel": "INFO",
                "resultado": "COMPATIBLE",
                "mensaje": "Todos los componentes seleccionados son compatibles entre sí."
            })

        return resultados_validacion