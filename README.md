# Global Energy Transition Dashboard

Dashboard interactivo desarrollado con Streamlit para analizar indicadores de
energía mundial entre 2000 y 2020.

Enlace del deploy: https://tb4dvgroup3.streamlit.app/

## Ejecución local

Ejecutar los siguientes comandos desde la raíz del repositorio.

### 1. Crear el entorno virtual

```bash
python3 -m venv .venv
```

### 2. Activar el entorno virtual

En macOS o Linux:

```bash
source .venv/bin/activate
```

En Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Instalar las dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Iniciar el dashboard

**Para ejecución local**

```bash
streamlit run dashboard/app.py
```

Streamlit mostrará en la terminal la dirección local para abrir el dashboard en
el navegador, normalmente `http://localhost:8501`.

Para desactivar el entorno virtual al terminar:

```bash
deactivate
```
