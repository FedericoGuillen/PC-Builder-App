from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .modelos import ConfiguracionPC

class ReglaCompatibilidadStrategy(ABC):
    """
    Interfaz abstracta (Patrón Strategy) para todas las reglas de compatibilidad del sistema.
    Cada regla concreta debe implementar el método 'evaluar'.
    """
    def __init__(self, id_regla: int, nombre: str, descripcion: str, codigo: str, nivel: str = "ERROR"):
        self.id_regla = id_regla
        self.nombre = nombre
        self.descripcion = descripcion
        self.codigo = codigo
        self.nivel = nivel  # 'INFO', 'ADVERTENCIA', 'ERROR'
        self.activa = True

    @abstractmethod
    def evaluar(self, configuracion: ConfiguracionPC) -> Optional[Dict[str, Any]]:
        """
        Evalúa la configuración de la PC según la regla de negocio.
        Retorna un diccionario con el resultado ('COMPATIBLE', 'ADVERTENCIA', 'INCOMPATIBLE') 
        y un mensaje explicativo, o None si la regla pasa sin problemas.
        """
        pass


class ReglaConsumoFuenteStrategy(ReglaCompatibilidadStrategy):
    """
    Verifica que la fuente de poder (PSU) instalada soporte el consumo total de vatios (watts) de los componentes.
    """
    def evaluar(self, configuracion: ConfiguracionPC) -> Optional[Dict[str, Any]]:
        consumo_total = configuracion.consumo_total_watts
        
        # Buscar si hay una fuente de poder agregada en la configuración
        fuente = next(
            (item.componente for item in configuracion.componentes_agregados 
             if item.componente.tipo.nombre.lower() in ["fuente de poder", "psu", "fuente"]), 
            None
        )
        
        if not fuente:
            return {
                "resultado": "INCOMPATIBLE",
                "nivel": self.nivel,
                "mensaje": "Falta agregar una fuente de poder (PSU) indispensable para alimentar los componentes."
            }
            
        # Extraemos los watts de la fuente desde el campo JSONB 'especificaciones'
        watts_fuente = fuente.especificaciones.get("watts", 0)
        
        if consumo_total > watts_fuente:
            return {
                "resultado": "INCOMPATIBLE",
                "nivel": self.nivel,
                "mensaje": f"El consumo estimado de los componentes ({consumo_total}W) supera la capacidad de la fuente seleccionada ({watts_fuente}W)."
            }
            
        return None  # Pasa la validación correctamente


class ReglaSocketCpuMotherboardStrategy(ReglaCompatibilidadStrategy):
    """
    Verifica que el socket del procesador (CPU) coincida con el socket de la placa madre (Motherboard).
    """
    def evaluar(self, configuracion: ConfiguracionPC) -> Optional[Dict[str, Any]]:
        cpu = next(
            (item.componente for item in configuracion.componentes_agregados 
             if item.componente.tipo.nombre.lower() in ["procesador", "cpu"]), 
            None
        )
        motherboard = next(
            (item.componente for item in configuracion.componentes_agregados 
             if item.componente.tipo.nombre.lower() in ["placa madre", "motherboard", "mainboard"]), 
            None
        )
        
        # Si falta alguno de los dos, esta regla específica no aplica todavía (lo maneja otra regla de componentes obligatorios)
        if not cpu or not motherboard:
            return None
            
        socket_cpu = cpu.especificaciones.get("socket")
        socket_mother = motherboard.especificaciones.get("socket")
        
        if socket_cpu and socket_mother and socket_cpu != socket_mother:
            return {
                "resultado": "INCOMPATIBLE",
                "nivel": self.nivel,
                "mensaje": f"Incompatibilidad de socket: El procesador requiere socket '{socket_cpu}' pero la placa madre tiene socket '{socket_mother}'."
            }
            
        return None