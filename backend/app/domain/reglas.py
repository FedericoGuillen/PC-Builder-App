from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .modelos import ConfiguracionPC

class ReglaCompatibilidadStrategy(ABC):
    """
    Interfaz abstracta (Patrón Strategy) para todas las reglas de compatibilidad del sistema.
    Cada regla concreta debe implementar el método 'evaluar'.
    """
    def __init__(self, id_regla: int = 0, nombre: str = "Regla Genérica", descripcion: str = "", codigo: str = "GENERIC", nivel: str = "ERROR"):
        self.id_regla = id_regla
        self.nombre = nombre
        self.descripcion = descripcion
        self.codigo = codigo
        self.nivel = nivel  # 'INFO', 'ADVERTENCIA', 'ERROR'
        self.activa = True

    @abstractmethod
    def evaluar(self, configuracion: ConfiguracionPC) -> Optional[Dict[str, Any]]:
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

class ReglaRamMotherboardStrategy(ReglaCompatibilidadStrategy):
    """
    Verifica que la tecnología de la memoria RAM (DDR4, DDR5, etc.) coincida con la placa madre.
    """
    def __init__(self):
        super().__init__(
            id_regla=3,
            nombre="RAM y Placa Madre",
            descripcion="Valida tecnología de RAM soportada por la Placa Madre",
            codigo="COMP_RAM_MOTHER"
        )

    def evaluar(self, configuracion: ConfiguracionPC) -> Optional[Dict[str, Any]]:
        motherboard = next(
            (item.componente for item in configuracion.componentes_agregados 
             if item.componente and item.componente.tipo and item.componente.tipo.nombre.lower() in ["placa madre", "motherboard", "mainboard"]), 
            None
        )
        rams = [
            item.componente for item in configuracion.componentes_agregados 
            if item.componente and item.componente.tipo and item.componente.tipo.nombre.lower() in ["memoria ram", "ram", "memoria"]
        ]

        if not motherboard or not rams:
            return None

        tipo_ram_mother = motherboard.especificaciones.get("tipo_ram")

        for ram in rams:
            tipo_ram = ram.especificaciones.get("tipo_ram")
            if tipo_ram_mother and tipo_ram and str(tipo_ram).upper() != str(tipo_ram_mother).upper():
                return {
                    "resultado": "INCOMPATIBLE",
                    "nivel": self.nivel,
                    "mensaje": f"La memoria RAM '{ram.nombre}' ({tipo_ram}) no es compatible con la placa madre '{motherboard.nombre}' (soporta {tipo_ram_mother})."
                }

        return None

class ReglaGabineteMotherboardStrategy(ReglaCompatibilidadStrategy):
    """
    Verifica que el factor de forma de la placa madre entre en el gabinete.
    """
    def __init__(self):
        super().__init__(
            id_regla=4,
            nombre="Gabinete y Placa Madre",
            descripcion="Valida factor de forma de la Placa Madre contra los soportados por el Gabinete",
            codigo="COMP_GABINETE_MOTHER"
        )

    def evaluar(self, configuracion: ConfiguracionPC) -> Optional[Dict[str, Any]]:
        motherboard = next(
            (item.componente for item in configuracion.componentes_agregados 
             if item.componente and item.componente.tipo and item.componente.tipo.nombre.lower() in ["placa madre", "motherboard", "mainboard"]), 
            None
        )
        gabinete = next(
            (item.componente for item in configuracion.componentes_agregados 
             if item.componente and item.componente.tipo and item.componente.tipo.nombre.lower() in ["gabinete", "case", "torre"]), 
            None
        )

        if not motherboard or not gabinete:
            return None

        factor_mother = motherboard.especificaciones.get("factor_forma")
        factores_soportados = gabinete.especificaciones.get("factores_forma_soportados", [])

        if factor_mother and factores_soportados:
            soportados_upper = [str(f).upper() for f in factores_soportados]
            if str(factor_mother).upper() not in soportados_upper:
                return {
                    "resultado": "INCOMPATIBLE",
                    "nivel": self.nivel,
                    "mensaje": f"La placa madre '{motherboard.nombre}' ({factor_mother}) no es compatible con el gabinete '{gabinete.nombre}' (soporta: {', '.join(factores_soportados)})."
                }

        return None