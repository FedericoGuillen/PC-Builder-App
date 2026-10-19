"""
Modelos ORM de SQLAlchemy mapeados directamente contra las tablas PostgreSQL de EnsamblaPC.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Boolean,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database.conexion import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    fecha_registro = Column(DateTime, nullable=False, default=datetime.utcnow)
    activo = Column(Boolean, nullable=False, default=True)

    configuraciones = relationship("ConfiguracionPC", back_populates="usuario", cascade="all, delete-orphan")


class Marca(Base):
    __tablename__ = "marcas"

    id_marca = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    sitio_web = Column(Text, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)

    componentes = relationship("Componente", back_populates="marca")


class TipoComponente(Base):
    __tablename__ = "tipos_componente"

    id_tipo = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    cantidad_maxima_sugerida = Column(Integer, nullable=False, default=1)
    obligatorio = Column(Boolean, nullable=False, default=False)

    componentes = relationship("Componente", back_populates="tipo")


class Componente(Base):
    __tablename__ = "componentes"

    id_componente = Column(BigInteger, primary_key=True, index=True)
    id_tipo = Column(BigInteger, ForeignKey("tipos_componente.id_tipo"), nullable=False)
    id_marca = Column(BigInteger, ForeignKey("marcas.id_marca"), nullable=False)
    nombre = Column(String(200), nullable=False)
    modelo = Column(String(150), nullable=True)
    descripcion = Column(Text, nullable=True)
    consumo_watts = Column(Integer, nullable=True)
    precio_referencia = Column(Numeric(12, 2), nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    especificaciones = Column(JSONB, nullable=False, default=dict)
    imagen_url = Column(Text, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.utcnow)

    marca = relationship("Marca", back_populates="componentes")
    tipo = relationship("TipoComponente", back_populates="componentes")
    configuraciones_asociadas = relationship("ConfiguracionComponente", back_populates="componente")


class ConfiguracionPC(Base):
    __tablename__ = "configuraciones_pc"

    id_configuracion = Column(BigInteger, primary_key=True, index=True)
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    estado = Column(String(20), nullable=False, default="BORRADOR")
    precio_total = Column(Numeric(12, 2), nullable=False, default=0.0)
    es_publica = Column(Boolean, nullable=False, default=False)
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="configuraciones")
    componentes_agregados = relationship("ConfiguracionComponente", back_populates="configuracion", cascade="all, delete-orphan")
    resultados_compatibilidad = relationship("ResultadoCompatibilidad", back_populates="configuracion", cascade="all, delete-orphan")

    @property
    def consumo_total_watts(self) -> int:
        """Calcula dinámicamente el consumo total sumando el consumo individual de cada pieza."""
        total = 0
        for item in self.componentes_agregados:
            if item.componente and item.componente.consumo_watts:
                total += item.componente.consumo_watts * item.cantidad
        return total


class ConfiguracionComponente(Base):
    __tablename__ = "configuracion_componentes"

    id_configuracion_componente = Column(BigInteger, primary_key=True, index=True)
    id_configuracion = Column(BigInteger, ForeignKey("configuraciones_pc.id_configuracion", ondelete="CASCADE"), nullable=False)
    id_componente = Column(BigInteger, ForeignKey("componentes.id_componente"), nullable=False)
    cantidad = Column(Integer, nullable=False, default=1)
    precio_al_seleccionar = Column(Numeric(12, 2), nullable=False)
    posicion_x = Column(Numeric(10, 2), nullable=True)
    posicion_y = Column(Numeric(10, 2), nullable=True)
    rotacion = Column(Numeric(6, 2), nullable=False, default=0.0)
    fecha_agregado = Column(DateTime, nullable=False, default=datetime.utcnow)

    configuracion = relationship("ConfiguracionPC", back_populates="componentes_agregados")
    componente = relationship("Componente", back_populates="configuraciones_asociadas")

    __table_args__ = (
        UniqueConstraint("id_configuracion", "id_componente", name="uq_configuracion_componente"),
    )


class ReglaCompatibilidad(Base):
    __tablename__ = "reglas_compatibilidad"

    id_regla = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=False)
    codigo = Column(String(100), nullable=False, unique=True)
    nivel = Column(String(20), nullable=False, default="ERROR")
    activa = Column(Boolean, nullable=False, default=True)

    resultados = relationship("ResultadoCompatibilidad", back_populates="regla")


class ResultadoCompatibilidad(Base):
    __tablename__ = "resultados_compatibilidad"

    id_resultado = Column(BigInteger, primary_key=True, index=True)
    id_configuracion = Column(BigInteger, ForeignKey("configuraciones_pc.id_configuracion", ondelete="CASCADE"), nullable=False)
    id_regla = Column(BigInteger, ForeignKey("reglas_compatibilidad.id_regla"), nullable=False)
    resultado = Column(String(20), nullable=False)
    mensaje = Column(Text, nullable=False)
    fecha_validacion = Column(DateTime, nullable=False, default=datetime.utcnow)

    configuracion = relationship("ConfiguracionPC", back_populates="resultados_compatibilidad")
    regla = relationship("ReglaCompatibilidad", back_populates="resultados")