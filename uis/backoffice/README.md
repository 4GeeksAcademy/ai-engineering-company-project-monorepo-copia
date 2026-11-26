# Backoffice de HealthCore

Interfaz web (Next.js) para analizar el fichero de incidencias: se sube el CSV, se ve el resumen en pantalla y se exportan los resultados. **No requiere inicio de sesión.**

## Requisitos

- Node.js 20 o posterior
- La API en marcha (ver `services/api/README.md`)

## Arranque

1. Arranca primero la API, en el puerto 8000:

   ```bash
   cd services/api
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -e .
   python -m uvicorn api.main:app --app-dir src --host 127.0.0.1 --port 8000
   ```

2. En otra terminal, arranca el backoffice:

   ```bash
   cd uis/backoffice
   npm install
   npm run dev
   ```

3. Abre `http://localhost:3000`, pulsa **Seleccionar fichero CSV**, elige `scripts/incidents-healthcore.csv` y pulsa **Analizar fichero**. Con ese fichero debe verse: 100 procesados, 94 válidos, 6 inválidos y satisfacción media 3.58. El botón **Exportar CSV** descarga las métricas.

## Configuración

No hay variables obligatorias. Si la API no está en `http://127.0.0.1:8000`, copia `.env.example` a `.env.local` y cambia `HEALTHCORE_API_URL`.

## Privacidad

La pantalla y el CSV exportado solo muestran métricas agregadas. Nunca aparecen identificadores de pacientes.
