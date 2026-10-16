Backend
Esta carpeta contendrá la lógica de negocio de la aplicación, las clases y los servicios necesarios para gestionar los componentes de PC y verificar su compatibilidad.

**Estructura del Backend**

El proyecto está modularizado dentro de la carpeta `backend/` para mantener separadas las responsabilidades del negocio y la interfaz web:

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

**Guía de Instalación y Ejecución**
1. Clonar el repositorio y abrir la terminal
Ubícate en la raíz del proyecto (tpfinal-poo3-grupo7/).

2. Crear y activar el entorno virtual
En Windows (CMD / PowerShell):

Bash
python -m venv venv
venv\Scripts\activate
En Linux / macOS (Terminal):

Bash
python3 -m venv venv
source venv/bin/activate

3. Instalar las dependencias
Instala automáticamente todas las librerías necesarias especificadas en el archivo del proyecto:

Bash
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

**Cómo Probar la API**
Abre tu navegador web y entra a la documentación interactiva de Swagger UI: http://127.0.0.1:8000/docs

Despliega el endpoint POST /api/v1/pc/validar-compatibilidad y haz clic en "Try it out".

Envía un JSON de prueba como el siguiente:

JSON
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

Presiona "Execute" para validar las reglas de negocio en tiempo real.

**Ejecución de Pruebas Unitarias (Pytest)**
Para correr las pruebas unitarias:

Windows: set PYTHONPATH=backend && pytest -v

Linux/Mac: PYTHONPATH=backend pytest -v