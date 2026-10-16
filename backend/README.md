# 🖥️ Guía Interactiva de Armado de PC - Backend (TP Final POO 3 - Grupo 7)

Backend desarrollado bajo una **Arquitectura en Capas** estricta (Dominio, Servicios y Controladores/API) aplicando Principios de Programación Orientada a Objetos (POO) y Patrones de Diseño.

---

## 📌 Descripción del Backend
Esta carpeta contiene la lógica de negocio de la aplicación, las clases y los servicios necesarios para gestionar los componentes de PC y verificar su compatibilidad.

---

## 📂 Estructura del Proyecto

El proyecto está modularizado dentro de la carpeta `backend/` para mantener separadas las responsabilidades del negocio y la interfaz web:

```text
tpfinal-poo3-grupo7/
│
├── backend/
│   ├── main.py                  # Servidor principal de FastAPI
│   └── app/
│       ├── domain/
│       │   ├── modelos.py       # Entidades del dominio (Usuario, Componente, ConfiguracionPC, etc.)
│       │   └── reglas.py        # Reglas de negocio y Patrón Strategy (Compatibilidad)
│       ├── services/
│       │   └── compatibilidad_service.py # Orquestador de casos de uso y validaciones
│       └── controllers/
│           └── pc_controller.py # Endpoints RESTful con FastAPI (Pydantic schemas)
│
├── tests/
│   └── test_compatibilidad.py   # Pruebas unitarias automatizadas con Pytest
│
├── requirements.txt             # Dependencias del proyecto
└── README.md                    # Documentación técnica

---
Guía de Instalación y Ejecución
1. Clonar el repositorio y abrir la terminal
Ubícate en la raíz del proyecto (tpfinal-poo3-grupo7/).

2. Crear y activar el entorno virtual

3. Instalar dependencias
pip install -r requirements.txt

4. Ejecutar el servidor Uvicorn
Para levantar la API web, ejecuta el siguiente comando desde la raíz:
En Windows (CMD / PowerShell):

Bash
set PYTHONPATH=backend
uvicorn backend.main:app --reload
En Linux / macOS (Terminal):

Bash
PYTHONPATH=backend uvicorn backend.main:app --reload

El servidor quedará corriendo en: http://127.0.0.1:8000

---
Cómo Probar la API
1. Abre tu navegador web y entra a la documentación interactiva de Swagger UI:
http://127.0.0.1:8000/docs

2. Despliega el endpoint POST /api/v1/pc/validar-compatibilidad y haz clic en "Try it out".

3. Envía un JSON de prueba como el siguiente:
{
  "nombre_configuracion": "PC de Prueba Grupo 7",
  "componentes": [
    {
      "id_componente": 1,
      "nombre": "Ryzen 5 7600",
      "tipo": "Procesador",
      "consumo_watts": 65,
      "precio": 250.0,
      "especificaciones": {
        "socket": "AM5"
      }
    },
    {
      "id_componente": 2,
      "nombre": "Prime H610M",
      "tipo": "Placa Madre",
      "consumo_watts": 25,
      "precio": 120.0,
      "especificaciones": {
        "socket": "LGA1700"
      }
    },
    {
      "id_componente": 3,
      "nombre": "Corsair CV400",
      "tipo": "Fuente de Poder",
      "consumo_watts": 0,
      "precio": 60.0,
      "especificaciones": {
        "watts": 400
      }
    }
  ]
}

4. Presiona "Execute" para validar las reglas de negocio en tiempo real.