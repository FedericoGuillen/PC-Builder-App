#!/usr/bin/env python
"""
seed_componentes.py
===================

Carga idempotente del catálogo de componentes de EnsamblaPC.

El script:

1. Verifica/crea las marcas y los tipos de componente necesarios.
2. Busca cada componente por (tipo, marca y modelo).
3. Inserta los que faltan.
4. Completa/actualiza las especificaciones técnicas de los existentes.
5. Normaliza claves JSONB que consumen las reglas de compatibilidad
   (`tipo_ram`, `factores_forma_soportados`, `watts`, `consumo_w`, etc.).

Uso:
    python seed_componentes.py
    python seed_componentes.py --dry-run
    python seed_componentes.py --sin-actualizar

Desde la raíz del repositorio también puede ejecutarse:
    python backend/seed_componentes.py

El script es idempotente: puede correrse todas las veces que sea necesario.
"""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError


# Permite ejecutar el script tanto desde backend/ como desde la raíz.
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Carga las variables de entorno antes de importar la conexión.
from dotenv import load_dotenv  # noqa: E402

load_dotenv(BASE_DIR / ".env")

from app.database.conexion import SessionLocal  # noqa: E402
from app.domain.modelos import Componente, Marca, TipoComponente  # noqa: E402


# ---------------------------------------------------------------------------
# Marcas
# ---------------------------------------------------------------------------

MARCAS: list[tuple[str, str]] = [
    ("AMD", "https://www.amd.com"),
    ("Intel", "https://www.intel.com"),
    ("ASUS", "https://www.asus.com"),
    ("MSI", "https://www.msi.com"),
    ("Gigabyte", "https://www.gigabyte.com"),
    ("NVIDIA", "https://www.nvidia.com"),
    ("Corsair", "https://www.corsair.com"),
    ("Kingston", "https://www.kingston.com"),
    ("Samsung", "https://www.samsung.com"),
    ("Western Digital", "https://www.westerndigital.com"),
    ("Cooler Master", "https://www.coolermaster.com"),
    ("DeepCool", "https://www.deepcool.com"),
    ("Noctua", "https://www.noctua.at"),
    ("EVGA", "https://www.evga.com"),
    ("NZXT", "https://nzxt.com"),
    ("Crucial", "https://www.crucial.com"),
    ("Seasonic", "https://seasonic.com"),
    ("be quiet!", "https://www.bequiet.com"),
    ("Thermalright", "https://www.thermalright.com"),
    ("Arctic", "https://www.arctic.de"),
]


# ---------------------------------------------------------------------------
# Tipos de componente
# ---------------------------------------------------------------------------

TIPOS: list[dict[str, Any]] = [
    {
        "nombre": "CPU",
        "descripcion": "Procesador principal del sistema",
        "cantidad_maxima_sugerida": 1,
        "obligatorio": True,
    },
    {
        "nombre": "CPU_COOLER",
        "descripcion": "Sistema de refrigeración para el procesador",
        "cantidad_maxima_sugerida": 1,
        "obligatorio": False,
    },
    {
        "nombre": "MOTHERBOARD",
        "descripcion": "Placa madre donde se conectan todos los componentes",
        "cantidad_maxima_sugerida": 1,
        "obligatorio": True,
    },
    {
        "nombre": "RAM",
        "descripcion": "Memoria principal del sistema",
        "cantidad_maxima_sugerida": 4,
        "obligatorio": True,
    },
    {
        "nombre": "STORAGE",
        "descripcion": "Dispositivos de almacenamiento SSD o HDD",
        "cantidad_maxima_sugerida": 8,
        "obligatorio": True,
    },
    {
        "nombre": "GPU",
        "descripcion": "Tarjeta gráfica dedicada",
        "cantidad_maxima_sugerida": 4,
        "obligatorio": False,
    },
    {
        "nombre": "PSU",
        "descripcion": "Fuente de alimentación",
        "cantidad_maxima_sugerida": 1,
        "obligatorio": True,
    },
    {
        "nombre": "CASE",
        "descripcion": "Gabinete que contiene los componentes",
        "cantidad_maxima_sugerida": 1,
        "obligatorio": True,
    },
]


# ---------------------------------------------------------------------------
# Catálogo de componentes
# ---------------------------------------------------------------------------

COMPONENTES: list[dict[str, Any]] = [
    # =======================================================================
    # CPUs AMD
    # =======================================================================
    {
        "tipo": "CPU",
        "marca": "AMD",
        "nombre": "AMD Ryzen 5 5600",
        "modelo": "5600",
        "descripcion": "Procesador AMD Ryzen 5 5600 de 6 núcleos para socket AM4.",
        "consumo_watts": 65,
        "precio_referencia": 150000,
        "stock": 12,
        "especificaciones": {
            "socket": "AM4",
            "arquitectura": "Zen 3",
            "nucleos": 6,
            "hilos": 12,
            "frecuencia_base": 3.5,
            "frecuencia_boost": 4.4,
            "cache_l3_mb": 32,
            "ram_tipo": ["DDR4"],
            "tipo_ram": "DDR4",
            "pcie": "4.0",
            "gpu_integrada": False,
            "tdp_w": 65,
            "consumo_w": 65,
        },
    },
    {
        "tipo": "CPU",
        "marca": "AMD",
        "nombre": "AMD Ryzen 5 7600",
        "modelo": "7600",
        "descripcion": "Procesador AMD Ryzen 5 7600 de 6 núcleos para socket AM5.",
        "consumo_watts": 65,
        "precio_referencia": 280000,
        "stock": 10,
        "especificaciones": {
            "socket": "AM5",
            "arquitectura": "Zen 4",
            "nucleos": 6,
            "hilos": 12,
            "frecuencia_base": 3.8,
            "frecuencia_boost": 5.1,
            "cache_l3_mb": 32,
            "ram_tipo": ["DDR5"],
            "tipo_ram": "DDR5",
            "pcie": "5.0",
            "gpu_integrada": True,
            "tdp_w": 65,
            "consumo_w": 65,
        },
    },
    {
        "tipo": "CPU",
        "marca": "AMD",
        "nombre": "AMD Ryzen 7 7800X3D",
        "modelo": "7800X3D",
        "descripcion": "Procesador AMD Ryzen 7 7800X3D con 3D V-Cache para gaming.",
        "consumo_watts": 120,
        "precio_referencia": 420000,
        "stock": 8,
        "especificaciones": {
            "socket": "AM5",
            "arquitectura": "Zen 4",
            "nucleos": 8,
            "hilos": 16,
            "frecuencia_base": 4.2,
            "frecuencia_boost": 5.0,
            "cache_l3_mb": 96,
            "ram_tipo": ["DDR5"],
            "tipo_ram": "DDR5",
            "pcie": "5.0",
            "gpu_integrada": True,
            "tdp_w": 120,
            "consumo_w": 120,
        },
    },
    # =======================================================================
    # CPUs Intel
    # =======================================================================
    {
        "tipo": "CPU",
        "marca": "Intel",
        "nombre": "Intel Core i5-12400F",
        "modelo": "12400F",
        "descripcion": "Procesador Intel Core i5-12400F de 6 núcleos para socket LGA1700.",
        "consumo_watts": 65,
        "precio_referencia": 160000,
        "stock": 15,
        "especificaciones": {
            "socket": "LGA1700",
            "arquitectura": "Alder Lake",
            "nucleos": 6,
            "hilos": 12,
            "frecuencia_base": 2.5,
            "frecuencia_boost": 4.4,
            "cache_l3_mb": 18,
            "ram_tipo": ["DDR4", "DDR5"],
            "pcie": "5.0",
            "gpu_integrada": False,
            "tdp_w": 65,
            "consumo_w": 65,
        },
    },
    {
        "tipo": "CPU",
        "marca": "Intel",
        "nombre": "Intel Core i5-13600K",
        "modelo": "13600K",
        "descripcion": "Procesador Intel Core i5-13600K de 14 núcleos para socket LGA1700.",
        "consumo_watts": 125,
        "precio_referencia": 300000,
        "stock": 10,
        "especificaciones": {
            "socket": "LGA1700",
            "arquitectura": "Raptor Lake",
            "nucleos": 14,
            "hilos": 20,
            "frecuencia_base": 3.5,
            "frecuencia_boost": 5.1,
            "cache_l3_mb": 24,
            "ram_tipo": ["DDR4", "DDR5"],
            "pcie": "5.0",
            "gpu_integrada": True,
            "tdp_w": 125,
            "consumo_w": 125,
        },
    },
    {
        "tipo": "CPU",
        "marca": "Intel",
        "nombre": "Intel Core i7-14700K",
        "modelo": "14700K",
        "descripcion": "Procesador Intel Core i7-14700K de 20 núcleos para socket LGA1700.",
        "consumo_watts": 125,
        "precio_referencia": 400000,
        "stock": 10,
        "especificaciones": {
            "socket": "LGA1700",
            "arquitectura": "Raptor Lake Refresh",
            "nucleos": 20,
            "hilos": 28,
            "frecuencia_base": 3.4,
            "frecuencia_boost": 5.6,
            "cache_l3_mb": 33,
            "ram_tipo": ["DDR4", "DDR5"],
            "pcie": "5.0",
            "gpu_integrada": True,
            "tdp_w": 125,
            "consumo_w": 125,
        },
    },
    # =======================================================================
    # Motherboards AM5
    # =======================================================================
    {
        "tipo": "MOTHERBOARD",
        "marca": "ASUS",
        "nombre": "ASUS TUF Gaming B650-PLUS WIFI",
        "modelo": "B650-PLUS WIFI",
        "descripcion": "Motherboard AM5 con chipset B650, WiFi 6 y DDR5.",
        "consumo_watts": 70,
        "precio_referencia": 250000,
        "stock": 10,
        "especificaciones": {
            "socket": "AM5",
            "chipset": "B650",
            "form_factor": "ATX",
            "factor_forma": "ATX",
            "ram_tipo": ["DDR5"],
            "tipo_ram": "DDR5",
            "ram_slots": 4,
            "ram_max_gb": 192,
            "pcie": "5.0",
            "m2_slots": 3,
            "consumo_w": 70,
        },
    },
    {
        "tipo": "MOTHERBOARD",
        "marca": "MSI",
        "nombre": "MSI MAG B650 Tomahawk WIFI",
        "modelo": "B650 Tomahawk WIFI",
        "descripcion": "Motherboard AM5 con chipset B650, WiFi 6E y DDR5.",
        "consumo_watts": 75,
        "precio_referencia": 280000,
        "stock": 10,
        "especificaciones": {
            "socket": "AM5",
            "chipset": "B650",
            "form_factor": "ATX",
            "factor_forma": "ATX",
            "ram_tipo": ["DDR5"],
            "tipo_ram": "DDR5",
            "ram_slots": 4,
            "ram_max_gb": 192,
            "pcie": "5.0",
            "m2_slots": 3,
            "consumo_w": 75,
        },
    },
    {
        "tipo": "MOTHERBOARD",
        "marca": "MSI",
        "nombre": "MSI MPG X670E Carbon WiFi",
        "modelo": "X670E CARBON WIFI",
        "descripcion": "Motherboard AM5 de gama alta con chipset X670E y PCIe 5.0.",
        "consumo_watts": 90,
        "precio_referencia": 420000,
        "stock": 6,
        "especificaciones": {
            "socket": "AM5",
            "chipset": "X670E",
            "form_factor": "ATX",
            "factor_forma": "ATX",
            "ram_tipo": ["DDR5"],
            "tipo_ram": "DDR5",
            "ram_slots": 4,
            "ram_max_gb": 192,
            "pcie": "5.0",
            "m2_slots": 4,
            "consumo_w": 90,
        },
    },
    {
        "tipo": "MOTHERBOARD",
        "marca": "ASUS",
        "nombre": "ASUS ROG Strix X670E-E Gaming WiFi",
        "modelo": "X670E-E GAMING WIFI",
        "descripcion": "Motherboard AM5 premium con chipset X670E y conectividad WiFi 6E.",
        "consumo_watts": 95,
        "precio_referencia": 480000,
        "stock": 5,
        "especificaciones": {
            "socket": "AM5",
            "chipset": "X670E",
            "form_factor": "ATX",
            "factor_forma": "ATX",
            "ram_tipo": ["DDR5"],
            "tipo_ram": "DDR5",
            "ram_slots": 4,
            "ram_max_gb": 192,
            "pcie": "5.0",
            "m2_slots": 4,
            "consumo_w": 95,
        },
    },
    # =======================================================================
    # Motherboards LGA1700
    # =======================================================================
    {
        "tipo": "MOTHERBOARD",
        "marca": "MSI",
        "nombre": "MSI PRO B660M-A DDR4",
        "modelo": "B660M-A DDR4",
        "descripcion": "Motherboard LGA1700 Micro-ATX con chipset B660 y soporte DDR4.",
        "consumo_watts": 65,
        "precio_referencia": 180000,
        "stock": 12,
        "especificaciones": {
            "socket": "LGA1700",
            "chipset": "B660",
            "form_factor": "Micro-ATX",
            "factor_forma": "Micro-ATX",
            "ram_tipo": ["DDR4"],
            "tipo_ram": "DDR4",
            "ram_slots": 4,
            "ram_max_gb": 128,
            "pcie": "4.0",
            "m2_slots": 2,
            "consumo_w": 65,
        },
    },
    {
        "tipo": "MOTHERBOARD",
        "marca": "Gigabyte",
        "nombre": "Gigabyte B760 Gaming X AX",
        "modelo": "B760 GAMING X AX",
        "descripcion": "Motherboard LGA1700 ATX con chipset B760, WiFi 6E y DDR5.",
        "consumo_watts": 80,
        "precio_referencia": 260000,
        "stock": 10,
        "especificaciones": {
            "socket": "LGA1700",
            "chipset": "B760",
            "form_factor": "ATX",
            "factor_forma": "ATX",
            "ram_tipo": ["DDR5"],
            "tipo_ram": "DDR5",
            "ram_slots": 4,
            "ram_max_gb": 192,
            "pcie": "5.0",
            "m2_slots": 3,
            "consumo_w": 80,
        },
    },
    {
        "tipo": "MOTHERBOARD",
        "marca": "ASUS",
        "nombre": "ASUS Prime Z790-P WIFI",
        "modelo": "Z790-P WIFI",
        "descripcion": "Motherboard Intel LGA1700 con chipset Z790, WiFi 6 y DDR5.",
        "consumo_watts": 80,
        "precio_referencia": 320000,
        "stock": 10,
        "especificaciones": {
            "socket": "LGA1700",
            "chipset": "Z790",
            "form_factor": "ATX",
            "factor_forma": "ATX",
            "ram_tipo": ["DDR5"],
            "tipo_ram": "DDR5",
            "ram_slots": 4,
            "ram_max_gb": 192,
            "pcie": "5.0",
            "m2_slots": 4,
            "consumo_w": 80,
        },
    },
    {
        "tipo": "MOTHERBOARD",
        "marca": "Gigabyte",
        "nombre": "Gigabyte Gaming X Z790 X AX",
        "modelo": "Z790 X AX",
        "descripcion": "Motherboard Intel LGA1700 con chipset Z790 y DDR5.",
        "consumo_watts": 75,
        "precio_referencia": 300000,
        "stock": 10,
        "especificaciones": {
            "socket": "LGA1700",
            "chipset": "Z790",
            "form_factor": "ATX",
            "factor_forma": "ATX",
            "ram_tipo": ["DDR5"],
            "tipo_ram": "DDR5",
            "ram_slots": 4,
            "ram_max_gb": 192,
            "pcie": "5.0",
            "m2_slots": 4,
            "consumo_w": 75,
        },
    },
    # =======================================================================
    # Memoria RAM
    # =======================================================================
    {
        "tipo": "RAM",
        "marca": "Kingston",
        "nombre": "Kingston Fury Beast DDR4-3200 8GB",
        "modelo": "DDR4-3200 8GB",
        "descripcion": "Módulo DDR4 de 8GB a 3200 MHz para equipos de entrada.",
        "consumo_watts": 6,
        "precio_referencia": 45000,
        "stock": 20,
        "especificaciones": {
            "tipo": "DDR4",
            "tipo_ram": "DDR4",
            "tipo_memoria": "DDR4",
            "capacidad_gb": 8,
            "modulos": 1,
            "velocidad_mhz": 3200,
            "latencia": "CL16",
            "consumo_w": 6,
        },
    },
    {
        "tipo": "RAM",
        "marca": "Corsair",
        "nombre": "Corsair Vengeance LPX DDR4-3200 16GB",
        "modelo": "DDR4-3200 16GB",
        "descripcion": "Kit 2x8GB DDR4 a 3200 MHz de perfil bajo.",
        "consumo_watts": 8,
        "precio_referencia": 70000,
        "stock": 18,
        "especificaciones": {
            "tipo": "DDR4",
            "tipo_ram": "DDR4",
            "tipo_memoria": "DDR4",
            "capacidad_gb": 16,
            "modulos": 2,
            "velocidad_mhz": 3200,
            "latencia": "CL16",
            "consumo_w": 8,
        },
    },
    {
        "tipo": "RAM",
        "marca": "Corsair",
        "nombre": "Corsair Vengeance LPX DDR4-3600 32GB",
        "modelo": "DDR4-3600 32GB",
        "descripcion": "Kit 2x16GB DDR4 a 3600 MHz para gaming y productividad.",
        "consumo_watts": 10,
        "precio_referencia": 120000,
        "stock": 12,
        "especificaciones": {
            "tipo": "DDR4",
            "tipo_ram": "DDR4",
            "tipo_memoria": "DDR4",
            "capacidad_gb": 32,
            "modulos": 2,
            "velocidad_mhz": 3600,
            "latencia": "CL18",
            "consumo_w": 10,
        },
    },
    {
        "tipo": "RAM",
        "marca": "Kingston",
        "nombre": "Kingston Fury Beast DDR5-5200 8GB",
        "modelo": "DDR5-5200 8GB",
        "descripcion": "Módulo DDR5 de 8GB a 5200 MHz para plataformas AM5 y LGA1700.",
        "consumo_watts": 6,
        "precio_referencia": 45000,
        "stock": 16,
        "especificaciones": {
            "tipo": "DDR5",
            "tipo_ram": "DDR5",
            "tipo_memoria": "DDR5",
            "capacidad_gb": 8,
            "modulos": 1,
            "velocidad_mhz": 5200,
            "latencia": "CL40",
            "consumo_w": 6,
        },
    },
    {
        "tipo": "RAM",
        "marca": "Kingston",
        "nombre": "Kingston Fury Beast DDR5-5600 32GB",
        "modelo": "DDR5-5600 32GB",
        "descripcion": "Kit 2x16GB DDR5 a 5600 MHz para gaming y productividad.",
        "consumo_watts": 10,
        "precio_referencia": 120000,
        "stock": 15,
        "especificaciones": {
            "tipo": "DDR5",
            "tipo_ram": "DDR5",
            "tipo_memoria": "DDR5",
            "capacidad_gb": 32,
            "modulos": 2,
            "velocidad_mhz": 5600,
            "latencia": "CL40",
            "consumo_w": 10,
        },
    },
    {
        "tipo": "RAM",
        "marca": "Kingston",
        "nombre": "Kingston Fury Beast DDR5-6000 32GB",
        "modelo": "DDR5-6000 32GB",
        "descripcion": "Kit 2x16GB DDR5 a 6000 MHz de alto rendimiento.",
        "consumo_watts": 10,
        "precio_referencia": 145000,
        "stock": 10,
        "especificaciones": {
            "tipo": "DDR5",
            "tipo_ram": "DDR5",
            "tipo_memoria": "DDR5",
            "capacidad_gb": 32,
            "modulos": 2,
            "velocidad_mhz": 6000,
            "latencia": "CL36",
            "consumo_w": 10,
        },
    },
    {
        "tipo": "RAM",
        "marca": "Samsung",
        "nombre": "Samsung DDR5-5600 16GB",
        "modelo": "DDR5-5600 16GB",
        "descripcion": "Kit 2x8GB DDR5 a 5600 MHz para equipos de entrada.",
        "consumo_watts": 8,
        "precio_referencia": 70000,
        "stock": 20,
        "especificaciones": {
            "tipo": "DDR5",
            "tipo_ram": "DDR5",
            "tipo_memoria": "DDR5",
            "capacidad_gb": 16,
            "modulos": 2,
            "velocidad_mhz": 5600,
            "latencia": "CL40",
            "consumo_w": 8,
        },
    },
    # =======================================================================
    # GPUs
    # =======================================================================
    {
        "tipo": "GPU",
        "marca": "NVIDIA",
        "nombre": "NVIDIA GeForce RTX 3060 12GB",
        "modelo": "RTX 3060 12GB",
        "descripcion": "Tarjeta gráfica para gaming en 1080p con 12GB de VRAM.",
        "consumo_watts": 170,
        "precio_referencia": 350000,
        "stock": 10,
        "especificaciones": {
            "vram_gb": 12,
            "tipo_memoria": "GDDR6",
            "pcie": "4.0 x16",
            "salidas_video": ["HDMI", "DisplayPort"],
            "longitud_mm": 242,
            "fuente_recomendada_w": 550,
            "consumo_w": 170,
        },
    },
    {
        "tipo": "GPU",
        "marca": "NVIDIA",
        "nombre": "NVIDIA GeForce RTX 4060 Ti 8GB",
        "modelo": "RTX 4060 Ti 8GB",
        "descripcion": "Tarjeta gráfica para gaming en 1080p y 1440p con DLSS 3.",
        "consumo_watts": 160,
        "precio_referencia": 550000,
        "stock": 9,
        "especificaciones": {
            "vram_gb": 8,
            "tipo_memoria": "GDDR6",
            "pcie": "4.0 x8",
            "salidas_video": ["HDMI", "DisplayPort"],
            "longitud_mm": 245,
            "fuente_recomendada_w": 550,
            "consumo_w": 160,
        },
    },
    {
        "tipo": "GPU",
        "marca": "AMD",
        "nombre": "AMD Radeon RX 6700 XT 12GB",
        "modelo": "RX 6700 XT 12GB",
        "descripcion": "Tarjeta gráfica AMD para gaming en 1440p con 12GB de VRAM.",
        "consumo_watts": 230,
        "precio_referencia": 480000,
        "stock": 8,
        "especificaciones": {
            "vram_gb": 12,
            "tipo_memoria": "GDDR6",
            "pcie": "4.0 x16",
            "salidas_video": ["HDMI", "DisplayPort"],
            "longitud_mm": 267,
            "fuente_recomendada_w": 650,
            "consumo_w": 230,
        },
    },
    {
        "tipo": "GPU",
        "marca": "NVIDIA",
        "nombre": "NVIDIA GeForce RTX 4070 12GB",
        "modelo": "RTX 4070 12GB",
        "descripcion": "Tarjeta gráfica para gaming en 1440p con DLSS 3 y 12GB de VRAM.",
        "consumo_watts": 200,
        "precio_referencia": 700000,
        "stock": 7,
        "especificaciones": {
            "vram_gb": 12,
            "tipo_memoria": "GDDR6X",
            "pcie": "4.0 x16",
            "salidas_video": ["HDMI", "DisplayPort"],
            "longitud_mm": 244,
            "fuente_recomendada_w": 650,
            "consumo_w": 200,
        },
    },
    # =======================================================================
    # Fuentes de poder
    # =======================================================================
    {
        "tipo": "PSU",
        "marca": "Cooler Master",
        "nombre": "Cooler Master MWE Gold 500 V2",
        "modelo": "MWE Gold 500 V2",
        "descripcion": "Fuente de alimentación 500W con certificación 80+ Gold.",
        "consumo_watts": 0,
        "precio_referencia": 90000,
        "stock": 15,
        "especificaciones": {
            "potencia_w": 500,
            "watts": 500,
            "certificacion": "80+ Gold",
            "modular": False,
            "factor_forma": "ATX",
            "consumo_w": 0,
        },
    },
    {
        "tipo": "PSU",
        "marca": "be quiet!",
        "nombre": "be quiet! Pure Power 12 M 550W",
        "modelo": "Pure Power 12 M 550W",
        "descripcion": "Fuente de alimentación 550W modular con certificación 80+ Gold.",
        "consumo_watts": 0,
        "precio_referencia": 120000,
        "stock": 12,
        "especificaciones": {
            "potencia_w": 550,
            "watts": 550,
            "certificacion": "80+ Gold",
            "modular": True,
            "factor_forma": "ATX",
            "consumo_w": 0,
        },
    },
    {
        "tipo": "PSU",
        "marca": "Corsair",
        "nombre": "Corsair RM650e",
        "modelo": "RM650e",
        "descripcion": "Fuente de alimentación 650W modular con certificación 80+ Gold.",
        "consumo_watts": 0,
        "precio_referencia": 120000,
        "stock": 10,
        "especificaciones": {
            "potencia_w": 650,
            "watts": 650,
            "certificacion": "80+ Gold",
            "modular": True,
            "factor_forma": "ATX",
            "consumo_w": 0,
        },
    },
    {
        "tipo": "PSU",
        "marca": "Seasonic",
        "nombre": "Seasonic Focus GX-750",
        "modelo": "Focus GX-750",
        "descripcion": "Fuente de alimentación 750W totalmente modular 80+ Gold.",
        "consumo_watts": 0,
        "precio_referencia": 160000,
        "stock": 10,
        "especificaciones": {
            "potencia_w": 750,
            "watts": 750,
            "certificacion": "80+ Gold",
            "modular": True,
            "factor_forma": "ATX",
            "consumo_w": 0,
        },
    },
    {
        "tipo": "PSU",
        "marca": "EVGA",
        "nombre": "EVGA SuperNOVA 750 G6",
        "modelo": "SuperNOVA 750 G6",
        "descripcion": "Fuente de alimentación 750W modular con certificación 80+ Gold.",
        "consumo_watts": 0,
        "precio_referencia": 150000,
        "stock": 10,
        "especificaciones": {
            "potencia_w": 750,
            "watts": 750,
            "certificacion": "80+ Gold",
            "modular": True,
            "factor_forma": "ATX",
            "consumo_w": 0,
        },
    },
    # =======================================================================
    # Almacenamiento
    # =======================================================================
    {
        "tipo": "STORAGE",
        "marca": "Crucial",
        "nombre": "Crucial P3 Plus 1TB",
        "modelo": "P3 Plus 1TB",
        "descripcion": "SSD NVMe PCIe 4.0 de 1TB para almacenamiento de alto rendimiento.",
        "consumo_watts": 5,
        "precio_referencia": 95000,
        "stock": 15,
        "especificaciones": {
            "tipo": "SSD_NVME",
            "capacidad_gb": 1000,
            "interfaz": "PCIe 4.0 x4",
            "factor_forma": "M.2 2280",
            "velocidad_lectura_mbps": 5000,
            "velocidad_escritura_mbps": 4200,
            "consumo_w": 5,
        },
    },
    {
        "tipo": "STORAGE",
        "marca": "Kingston",
        "nombre": "Kingston NV2 500GB",
        "modelo": "NV2 500GB",
        "descripcion": "SSD NVMe PCIe 4.0 de 500GB para equipos de entrada.",
        "consumo_watts": 4,
        "precio_referencia": 55000,
        "stock": 20,
        "especificaciones": {
            "tipo": "SSD_NVME",
            "capacidad_gb": 500,
            "interfaz": "PCIe 4.0 x4",
            "factor_forma": "M.2 2280",
            "velocidad_lectura_mbps": 3500,
            "velocidad_escritura_mbps": 2100,
            "consumo_w": 4,
        },
    },
    {
        "tipo": "STORAGE",
        "marca": "Samsung",
        "nombre": "Samsung 870 EVO 1TB",
        "modelo": "870 EVO 1TB",
        "descripcion": "SSD SATA III de 1TB para almacenamiento general.",
        "consumo_watts": 3,
        "precio_referencia": 90000,
        "stock": 18,
        "especificaciones": {
            "tipo": "SSD_SATA",
            "capacidad_gb": 1000,
            "interfaz": "SATA III",
            "factor_forma": "2.5",
            "velocidad_lectura_mbps": 560,
            "velocidad_escritura_mbps": 530,
            "consumo_w": 3,
        },
    },
    {
        "tipo": "STORAGE",
        "marca": "Samsung",
        "nombre": "Samsung SSD 990 PRO 1TB",
        "modelo": "990 PRO 1TB",
        "descripcion": "SSD NVMe PCIe 4.0 de alto rendimiento.",
        "consumo_watts": 6,
        "precio_referencia": 120000,
        "stock": 15,
        "especificaciones": {
            "tipo": "SSD_NVME",
            "capacidad_gb": 1000,
            "interfaz": "PCIe 4.0 x4",
            "factor_forma": "M.2 2280",
            "velocidad_lectura_mbps": 7450,
            "velocidad_escritura_mbps": 6900,
            "consumo_w": 6,
        },
    },
    # =======================================================================
    # Gabinetes
    # =======================================================================
    {
        "tipo": "CASE",
        "marca": "NZXT",
        "nombre": "NZXT H5 Flow",
        "modelo": "H5 Flow",
        "descripcion": "Gabinete ATX con panel frontal de alto flujo de aire.",
        "consumo_watts": 0,
        "precio_referencia": 120000,
        "stock": 10,
        "especificaciones": {
            "form_factor": ["ATX", "Micro-ATX", "Mini-ITX"],
            "factores_forma_soportados": ["ATX", "Micro-ATX", "Mini-ITX"],
            "gpu_max_mm": 365,
            "cpu_cooler_max_mm": 165,
            "radiador_frontal_mm": 280,
            "radiador_superior_mm": 240,
            "consumo_w": 0,
        },
    },
    {
        "tipo": "CASE",
        "marca": "NZXT",
        "nombre": "NZXT H7 Flow",
        "modelo": "H7 Flow",
        "descripcion": "Gabinete ATX de gran formato con excelente flujo de aire.",
        "consumo_watts": 0,
        "precio_referencia": 180000,
        "stock": 8,
        "especificaciones": {
            "form_factor": ["ATX", "Micro-ATX", "Mini-ITX"],
            "factores_forma_soportados": ["ATX", "Micro-ATX", "Mini-ITX"],
            "gpu_max_mm": 400,
            "cpu_cooler_max_mm": 185,
            "radiador_frontal_mm": 360,
            "radiador_superior_mm": 360,
            "consumo_w": 0,
        },
    },
    {
        "tipo": "CASE",
        "marca": "Corsair",
        "nombre": "Corsair 3000D Airflow",
        "modelo": "3000D Airflow",
        "descripcion": "Gabinete ATX compacto optimizado para refrigeración.",
        "consumo_watts": 0,
        "precio_referencia": 110000,
        "stock": 12,
        "especificaciones": {
            "form_factor": ["ATX", "Micro-ATX", "Mini-ITX"],
            "factores_forma_soportados": ["ATX", "Micro-ATX", "Mini-ITX"],
            "gpu_max_mm": 360,
            "cpu_cooler_max_mm": 170,
            "radiador_frontal_mm": 360,
            "radiador_superior_mm": 240,
            "consumo_w": 0,
        },
    },
    {
        "tipo": "CASE",
        "marca": "Cooler Master",
        "nombre": "Cooler Master NR200P",
        "modelo": "NR200P",
        "descripcion": "Gabinete Mini-ITX compacto con soporte para radiador lateral.",
        "consumo_watts": 0,
        "precio_referencia": 130000,
        "stock": 9,
        "especificaciones": {
            "form_factor": ["Mini-ITX"],
            "factores_forma_soportados": ["Mini-ITX"],
            "gpu_max_mm": 330,
            "cpu_cooler_max_mm": 155,
            "radiador_lateral_mm": 280,
            "consumo_w": 0,
        },
    },
    {
        "tipo": "CASE",
        "marca": "Corsair",
        "nombre": "Corsair 4000D Airflow",
        "modelo": "4000D Airflow",
        "descripcion": "Gabinete ATX optimizado para refrigeración.",
        "consumo_watts": 0,
        "precio_referencia": 140000,
        "stock": 10,
        "especificaciones": {
            "form_factor": ["ATX", "Micro-ATX", "Mini-ITX"],
            "factores_forma_soportados": ["ATX", "Micro-ATX", "Mini-ITX"],
            "gpu_max_mm": 360,
            "cpu_cooler_max_mm": 170,
            "radiador_frontal_mm": 360,
            "radiador_superior_mm": 280,
            "consumo_w": 0,
        },
    },
    # =======================================================================
    # Disipadores / Coolers
    # =======================================================================
    {
        "tipo": "CPU_COOLER",
        "marca": "Noctua",
        "nombre": "Noctua NH-D15",
        "modelo": "NH-D15",
        "descripcion": "Disipador de aire de doble torre con dos ventiladores de 140mm.",
        "consumo_watts": 2,
        "precio_referencia": 160000,
        "stock": 8,
        "especificaciones": {
            "tipo": "AIRE",
            "socket": ["AM4", "AM5", "LGA1700", "LGA1200"],
            "tdp_max": 250,
            "altura_mm": 165,
            "ventiladores": 2,
            "consumo_w": 2,
        },
    },
    {
        "tipo": "CPU_COOLER",
        "marca": "Thermalright",
        "nombre": "Thermalright Peerless Assassin 120 SE",
        "modelo": "Peerless Assassin 120 SE",
        "descripcion": "Disipador de aire de doble torre con relación precio/rendimiento destacada.",
        "consumo_watts": 3,
        "precio_referencia": 60000,
        "stock": 15,
        "especificaciones": {
            "tipo": "AIRE",
            "socket": ["AM4", "AM5", "LGA1700", "LGA1200"],
            "tdp_max": 265,
            "altura_mm": 155,
            "ventiladores": 2,
            "consumo_w": 3,
        },
    },
    {
        "tipo": "CPU_COOLER",
        "marca": "Arctic",
        "nombre": "Arctic Liquid Freezer III 240",
        "modelo": "Liquid Freezer III 240",
        "descripcion": "Refrigeración líquida AIO de 240mm con bomba de alto rendimiento.",
        "consumo_watts": 7,
        "precio_referencia": 140000,
        "stock": 10,
        "especificaciones": {
            "tipo": "LIQUIDO",
            "socket": ["AM4", "AM5", "LGA1700", "LGA1200"],
            "tdp_max": 300,
            "radiador_mm": 240,
            "ventiladores": 2,
            "consumo_w": 7,
        },
    },
    {
        "tipo": "CPU_COOLER",
        "marca": "Cooler Master",
        "nombre": "Cooler Master Hyper 212 Black Edition",
        "modelo": "Black Edition",
        "descripcion": "Cooler por aire compatible con AM5 y LGA1700.",
        "consumo_watts": 3,
        "precio_referencia": 65000,
        "stock": 10,
        "especificaciones": {
            "tipo": "AIRE",
            "socket": ["AM5", "LGA1700"],
            "tdp_max": 180,
            "altura_mm": 159,
            "ventiladores": 1,
            "consumo_w": 3,
        },
    },
]


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def obtener_o_crear_marca(session, nombre: str, sitio_web: str) -> Marca:
    marca = session.execute(
        select(Marca).where(func.lower(Marca.nombre) == nombre.lower())
    ).scalars().first()

    if marca is None:
        marca = Marca(nombre=nombre, sitio_web=sitio_web, activo=True)
        session.add(marca)
        session.flush()
        print(f"  + Marca creada: {nombre}")

    return marca


def obtener_o_crear_tipo(session, datos: dict[str, Any]) -> TipoComponente:
    tipo = session.execute(
        select(TipoComponente).where(
            func.lower(TipoComponente.nombre) == datos["nombre"].lower()
        )
    ).scalars().first()

    if tipo is None:
        tipo = TipoComponente(**datos)
        session.add(tipo)
        session.flush()
        print(f"  + Tipo creado: {datos['nombre']}")

    return tipo


def buscar_componente(
    session,
    id_tipo: int,
    id_marca: int,
    modelo: str,
) -> Componente | None:
    consulta = select(Componente).where(
        Componente.id_tipo == id_tipo,
        Componente.id_marca == id_marca,
        func.lower(func.trim(Componente.modelo)) == modelo.strip().lower(),
    )
    return session.execute(consulta).scalars().first()


def normalizar_especificaciones(componente: Componente) -> bool:
    """
    Agrega las claves JSONB que consumen las reglas y los repositorios.

    No pisa valores existentes: solo completa las claves faltantes.
    Devuelve True si modificó las especificaciones.
    """
    tipo = (componente.tipo.nombre or "").upper()
    especificaciones = dict(componente.especificaciones or {})
    cambios = False

    def completar(clave: str, valor: Any) -> None:
        nonlocal cambios

        if valor is None:
            return

        actual = especificaciones.get(clave)

        if actual is None or actual == "" or actual == []:
            especificaciones[clave] = valor
            cambios = True

    if componente.consumo_watts is not None:
        completar("consumo_w", componente.consumo_watts)

    if tipo == "MOTHERBOARD":
        ram_tipo = especificaciones.get("ram_tipo")

        if isinstance(ram_tipo, str):
            completar("tipo_ram", ram_tipo)
        elif isinstance(ram_tipo, list) and len(ram_tipo) == 1:
            # La regla compara un único valor. Si la placa soporta varias
            # tecnologías, se deja sin normalizar para no generar un falso
            # incompatible.
            completar("tipo_ram", ram_tipo[0])

        completar("factor_forma", especificaciones.get("form_factor"))

    elif tipo == "RAM":
        completar("tipo_ram", especificaciones.get("tipo"))
        completar("tipo_memoria", especificaciones.get("tipo"))

    elif tipo == "CASE":
        completar(
            "factores_forma_soportados",
            especificaciones.get("form_factor"),
        )

    elif tipo == "PSU":
        completar("watts", especificaciones.get("potencia_w"))
        completar("potencia_w", especificaciones.get("watts"))

    if cambios:
        componente.especificaciones = especificaciones

    return cambios


def resumen_por_categoria(session) -> None:
    consulta = (
        select(TipoComponente.nombre, func.count(Componente.id_componente))
        .outerjoin(
            Componente,
            (Componente.id_tipo == TipoComponente.id_tipo)
            & (Componente.activo.is_(True)),
        )
        .group_by(TipoComponente.nombre)
        .order_by(TipoComponente.nombre)
    )

    print("\nComponentes activos por categoría:")
    for nombre, total in session.execute(consulta).all():
        print(f"  {nombre:<15} {total:>3}")


def verificar_minimos(session) -> bool:
    """
    Comprueba los mínimos solicitados: 3 opciones por categoría principal
    y variedad por plataforma (AMD/Intel, AM5/LGA1700, DDR4/DDR5).
    """
    categorias = {
        "CPU": "CPU",
        "CPU_COOLER": "CPU_COOLER",
        "MOTHERBOARD": "MOTHERBOARD",
        "RAM": "RAM",
        "STORAGE": "STORAGE",
        "GPU": "GPU",
        "PSU": "PSU",
        "CASE": "CASE",
    }

    conteos = dict(
        session.execute(
            select(TipoComponente.nombre, func.count(Componente.id_componente))
            .join(Componente, Componente.id_tipo == TipoComponente.id_tipo)
            .where(Componente.activo.is_(True))
            .group_by(TipoComponente.nombre)
        ).all()
    )

    ok = True
    print("\nVerificación de mínimos por categoría:")
    for etiqueta, tipo in categorias.items():
        total = conteos.get(tipo, 0)
        estado = "OK" if total >= 3 else "FALTA"
        print(f"  {etiqueta:<15} {total:>3}  {estado}")
        if total < 3:
            ok = False

    def contar_por_json(campo: str, valor: str, tipo: str) -> int:
        consulta = (
            select(func.count(Componente.id_componente))
            .join(TipoComponente, TipoComponente.id_tipo == Componente.id_tipo)
            .where(
                TipoComponente.nombre == tipo,
                Componente.activo.is_(True),
                Componente.especificaciones.op("->>")(campo) == valor,
            )
        )
        return session.execute(consulta).scalar_one()

    def contar_por_marca(marca: str) -> int:
        consulta = (
            select(func.count(Componente.id_componente))
            .join(TipoComponente, TipoComponente.id_tipo == Componente.id_tipo)
            .join(Marca, Marca.id_marca == Componente.id_marca)
            .where(
                TipoComponente.nombre == "CPU",
                Componente.activo.is_(True),
                func.lower(Marca.nombre) == marca.lower(),
            )
        )
        return session.execute(consulta).scalar_one()

    controles = [
        ("CPU AMD", contar_por_marca("AMD")),
        ("CPU Intel", contar_por_marca("Intel")),
        ("Motherboards AM5", contar_por_json("socket", "AM5", "MOTHERBOARD")),
        (
            "Motherboards LGA1700",
            contar_por_json("socket", "LGA1700", "MOTHERBOARD"),
        ),
        ("RAM DDR4", contar_por_json("tipo_ram", "DDR4", "RAM")),
        ("RAM DDR5", contar_por_json("tipo_ram", "DDR5", "RAM")),
    ]

    print("\nVerificación de variedad:")
    for etiqueta, total in controles:
        estado = "OK" if total >= 3 else "FALTA"
        print(f"  {etiqueta:<22} {total:>3}  {estado}")
        if total < 3:
            ok = False

    return ok


# ---------------------------------------------------------------------------
# Proceso principal
# ---------------------------------------------------------------------------

def cargar_catalogo(
    actualizar_existentes: bool = True,
    dry_run: bool = False,
) -> bool:
    creados = 0
    actualizados = 0
    sin_cambios = 0

    with SessionLocal() as session:
        try:
            print("Verificando marcas...")
            marcas = {
                nombre: obtener_o_crear_marca(session, nombre, sitio)
                for nombre, sitio in MARCAS
            }

            print("Verificando tipos de componente...")
            tipos = {
                datos["nombre"]: obtener_o_crear_tipo(session, datos)
                for datos in TIPOS
            }

            print("\nVerificando catálogo de componentes...")
            for datos in COMPONENTES:
                tipo = tipos[datos["tipo"]]
                marca = marcas[datos["marca"]]
                componente = buscar_componente(
                    session,
                    tipo.id_tipo,
                    marca.id_marca,
                    datos["modelo"],
                )

                if componente is None:
                    componente = Componente(
                        id_tipo=tipo.id_tipo,
                        id_marca=marca.id_marca,
                        nombre=datos["nombre"],
                        modelo=datos["modelo"],
                        descripcion=datos["descripcion"],
                        consumo_watts=datos["consumo_watts"],
                        precio_referencia=Decimal(
                            str(datos["precio_referencia"])
                        ),
                        stock=datos["stock"],
                        especificaciones=dict(datos["especificaciones"]),
                        activo=True,
                    )
                    session.add(componente)
                    creados += 1
                    print(
                        f"  + {datos['tipo']:<12} "
                        f"{datos['marca']:<14} {datos['nombre']}"
                    )
                    continue

                if not actualizar_existentes:
                    normalizar_especificaciones(componente)
                    sin_cambios += 1
                    continue

                especificaciones_actuales = dict(
                    componente.especificaciones or {}
                )
                especificaciones_nuevas = dict(datos["especificaciones"])
                # Las claves del catálogo son la fuente de verdad técnica,
                # pero se conservan claves extra que no estén definidas.
                especificaciones_finales = {
                    **especificaciones_actuales,
                    **especificaciones_nuevas,
                }

                hubo_cambios = (
                    especificaciones_finales != especificaciones_actuales
                )

                if hubo_cambios:
                    componente.especificaciones = especificaciones_finales
                    actualizados += 1

                if datos["consumo_watts"] is not None:
                    if componente.consumo_watts != datos["consumo_watts"]:
                        componente.consumo_watts = datos["consumo_watts"]
                        hubo_cambios = True

                normalizar_especificaciones(componente)

                if hubo_cambios:
                    print(
                        f"  ~ {datos['tipo']:<12} "
                        f"{datos['marca']:<14} {datos['nombre']}"
                    )
                else:
                    sin_cambios += 1

            # Completa claves de compatibilidad en componentes históricos
            # que no forman parte de la lista canónica.
            print("\nNormalizando especificaciones históricas...")
            normalizados = 0
            for componente in session.execute(select(Componente)).scalars():
                if normalizar_especificaciones(componente):
                    normalizados += 1

            session.flush()
            resumen_por_categoria(session)
            minimos_ok = verificar_minimos(session)

            print("\nResumen de la carga:")
            print(f"  Componentes insertados:   {creados}")
            print(f"  Componentes actualizados: {actualizados}")
            print(f"  Sin cambios:              {sin_cambios}")
            print(f"  Specs normalizadas:       {normalizados}")

            if dry_run:
                session.rollback()
                print("\nDRY-RUN: transacción revertida, sin cambios guardados.")
            else:
                session.commit()
                print("\nCambios confirmados en la base de datos.")

            return minimos_ok

        except SQLAlchemyError as error:
            session.rollback()
            print(
                "\nERROR: no se pudo completar la carga del catálogo.",
                file=sys.stderr,
            )
            print(f"Detalle: {error}", file=sys.stderr)
            raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Carga idempotente del catálogo de componentes de EnsamblaPC.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra los cambios y hace rollback al finalizar.",
    )
    parser.add_argument(
        "--sin-actualizar",
        action="store_true",
        help="Solo inserta componentes faltantes; no actualiza especificaciones.",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("EnsamblaPC - Carga del catálogo de componentes")
    print("=" * 70)

    if args.dry_run:
        print("Modo DRY-RUN: los cambios no se guardarán.\n")

    try:
        minimos_ok = cargar_catalogo(
            actualizar_existentes=not args.sin_actualizar,
            dry_run=args.dry_run,
        )

        if args.dry_run:
            print("\nDRY-RUN completado. No se guardaron cambios.")
        else:
            print("\nCatálogo cargado correctamente.")

        if not minimos_ok:
            print(
                "\nADVERTENCIA: todavía no se alcanzaron los mínimos "
                "solicitados en todas las categorías.",
                file=sys.stderr,
            )
            return 1

        return 0

    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.", file=sys.stderr)
        return 130
    except Exception as error:  # noqa: BLE001
        print(f"\nERROR inesperado: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
