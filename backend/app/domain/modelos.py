from datetime import datetime
from typing import List, Dict, Optional, Any

class Usuario:
    def __init__(self, id_usuario: int, nombre: str, apellido: Optional[str], email: str, password_hash: str, activo: bool = True):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.password_hash = password_hash
        self.fecha_registro = datetime.now()
        self.activo = activo

    def cambiar_estado(self, estado: bool):
        self.activo = estado

    def __str__(self):
        return f"Usuario: {self.nombre} {self.apellido or ''} ({self.email})"


class Marca:
    def __init__(self, id_marca: int, nombre: str, sitio_web: Optional[str] = None, activo: bool = True):
        self.id_marca = id_marca
        self.nombre = nombre
        self.sitio_web = sitio_web
        self.activo = activo

    def __str__(self):
        return self.nombre


class TipoComponente:
    def __init__(self, id_tipo: int, nombre: str, descripcion: Optional[str] = None, cantidad_maxima_sugerida: int = 1, obligatorio: bool = False):
        self.id_tipo = id_tipo
        self.nombre = nombre
        self.descripcion = descripcion
        self.cantidad_maxima_sugerida = cantidad_maxima_sugerida
        self.obligatorio = obligatorio

    def __str__(self):
        return self.nombre


class Componente:
    def __init__(
        self, 
        id_componente: int, 
        tipo: TipoComponente, 
        marca: Marca, 
        nombre: str, 
        modelo: Optional[str], 
        descripcion: Optional[str], 
        consumo_watts: Optional[int], 
        precio_referencia: float, 
        stock: int, 
        especificaciones: Dict[str, Any], 
        imagen_url: Optional[str] = None
    ):
        self.id_componente = id_componente
        self.tipo = tipo
        self.marca = marca
        self.nombre = nombre
        self.modelo = modelo
        self.descripcion = descripcion
        self.consumo_watts = consumo_watts or 0
        self.precio_referencia = precio_referencia
        self.stock = stock
        self.especificaciones = especificaciones  # Mapeo directo del JSONB de la DB
        self.imagen_url = imagen_url
        self.activo = True
        self.fecha_creacion = datetime.now()

    def actualizar_stock(self, cantidad: int):
        if self.stock + cantidad >= 0:
            self.stock += cantidad
        else:
            raise ValueError(f"Stock insuficiente para el componente '{self.nombre}'.")

    def __str__(self):
        return f"[{self.marca.nombre}] {self.nombre} - ${self.precio_referencia}"


class ConfiguracionComponente:
    """
    Representa la tabla intermedia 'configuracion_componentes'.
    Vincula la PC con el componente y guarda datos específicos del armado (como posición visual y precio histórico).
    """
    def __init__(
        self, 
        componente: Componente, 
        cantidad: int = 1, 
        posicion_x: Optional[float] = None, 
        posicion_y: Optional[float] = None, 
        rotacion: float = 0.0
    ):
        self.componente = componente
        self.cantidad = cantidad
        self.precio_al_seleccionar = componente.precio_referencia  # Congela el precio al elegirlo
        self.posicion_x = posicion_x
        self.posicion_y = posicion_y
        self.rotacion = rotacion
        self.fecha_agregado = datetime.now()

    @property
    def subtotal(self) -> float:
        return self.precio_al_seleccionar * self.cantidad


class ConfiguracionPC:
    """
    Representa la tabla 'configuraciones_pc' y maneja la lógica de los componentes de la PC del usuario.
    """
    def __init__(self, id_configuracion: int, usuario: Usuario, nombre: str, descripcion: Optional[str] = None):
        self.id_configuracion = id_configuracion
        self.usuario = usuario
        self.nombre = nombre
        self.descripcion = descripcion
        self.estado = "BORRADOR"  # BORRADOR, COMPLETA, INCOMPATIBLE, FINALIZADA
        self.es_publica = False
        self.componentes_agregados: List[ConfiguracionComponente] = []
        self.fecha_creacion = datetime.now()
        self.fecha_modificacion = datetime.now()

    def agregar_componente(self, componente: Componente, cantidad: int = 1, x: Optional[float] = None, y: Optional[float] = None, rotacion: float = 0.0):
        # Si ya existe en la configuración, actualizamos su cantidad en lugar de duplicarlo
        for item in self.componentes_agregados:
            if item.componente.id_componente == componente.id_componente:
                item.cantidad += cantidad
                self.fecha_modificacion = datetime.now()
                return

        nuevo_item = ConfiguracionComponente(componente, cantidad, x, y, rotacion)
        self.componentes_agregados.append(nuevo_item)
        self.fecha_modificacion = datetime.now()

    def quitar_componente(self, id_componente: int):
        self.componentes_agregados = [
            item for item in self.componentes_agregados 
            if item.componente.id_componente != id_componente
        ]
        self.fecha_modificacion = datetime.now()

    @property
    def precio_total(self) -> float:
        return sum(item.subtotal for item in self.componentes_agregados)

    @property
    def consumo_total_watts(self) -> int:
        return sum(item.componente.consumo_watts * item.cantidad for item in self.componentes_agregados)

    def cambiar_estado(self, nuevo_estado: str):
        estados_validos = ["BORRADOR", "COMPLETA", "INCOMPATIBLE", "FINALIZADA"]
        if nuevo_estado in estados_validos:
            self.estado = nuevo_estado
            self.fecha_modificacion = datetime.now()
        else:
            raise ValueError(f"Estado '{nuevo_estado}' no válido para la configuración.")

    def __str__(self):
        return f"PC: '{self.nombre}' | Usuario: {self.usuario.nombre} | Estado: {self.estado} | Total: ${self.precio_total}"