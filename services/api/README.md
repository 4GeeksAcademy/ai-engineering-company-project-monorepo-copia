# API de HealthCore

Backend FastAPI para el análisis de incidencias. La API y el script `scripts/analyze.py` usan la misma lógica, en `src/api/incidents/analysis.py`.

**No requiere autenticación ni variables de entorno.** Ver `.env.example`.

## Requisitos

- Python 3.11 o posterior

## Instalación y arranque

Desde la raíz del repositorio:

```bash
cd services/api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m uvicorn api.main:app --app-dir src --reload --host 127.0.0.1 --port 8000
```

La API queda en `http://127.0.0.1:8000`. La documentación interactiva está en `http://127.0.0.1:8000/docs`. El backoffice (`uis/backoffice`, puerto 3000) reenvía `/api/*` a esta API.

## Endpoints

- `POST /api/incidents/analyze`: recibe `file` como `multipart/form-data` (un CSV) y devuelve el resumen en JSON.
- `GET /api/incidents/results/export`: descarga `resultados_healthcore.csv` (columnas `metric,value,percentage`) con el último análisis correcto.

Errores: fichero ausente, vacío, sin extensión `.csv`, no UTF-8 o sin las columnas obligatorias devuelven `400` con un mensaje en español. Exportar antes de analizar devuelve `404`.

Ejemplo:

```bash
curl -F "file=@../../scripts/incidents-healthcore.csv" http://127.0.0.1:8000/api/incidents/analyze
curl -OJ http://127.0.0.1:8000/api/incidents/results/export
```

El último resultado vive en memoria y se pierde al reiniciar el proceso; ejecútalo con un único worker.

## Script de línea de comandos

Desde la raíz del repositorio:

```bash
python scripts/analyze.py scripts/incidents-healthcore.csv
```

Al final pregunta `Export results to CSV? [y / n]`; con `y` guarda `results.csv`.

## Tests

Desde `services/api`, con el entorno activado:

```bash
python -m unittest discover -s tests -v
```

## Esquema del CSV

Codificación UTF-8, separador coma y fila de encabezado. Briefing completo en `scripts/incidents-BRIEFING.es.md`.

- **Campos:** `incident_id`, `date`, `clinic_id`, `country`, `category`, `description`, `status`, `patient_id`, `satisfaction_score` (obligatorio solo si `status` es `CLOSED`).
- **Clínicas:** `US-TX-01`, `US-TX-02`, `US-TX-03`, `US-FL-01`, `US-FL-02`, `US-FL-03`, `US-GA-01`, `US-GA-02`, `US-GA-03` (US); `UK-LON-01`, `UK-LON-02`, `UK-MAN-01` (UK). `country` debe coincidir con la clínica.
- **Categorías:** `APPOINTMENT`, `BILLING`, `CLINICAL_CARE`, `ACCESSIBILITY`, `ADMINISTRATIVE`.
- **Estados:** `OPEN`, `CLOSED`, `DISCARDED`.

## Registros inválidos

Se cuentan por regla y se excluyen del análisis: `clinic_id` faltante o inválido; país que no coincide con la clínica; categoría faltante o inválida; descripción vacía o de menos de 5 caracteres; `patient_id` ausente o fuera del formato `PAT-XXXXXX`; caso `CLOSED` sin puntaje; puntaje fuera de 1–5. Además se cuentan estados no válidos y filas con columnas de más.

## Privacidad

`patient_id` es información protegida (HIPAA / UK GDPR). Nunca se imprime, registra ni exporta; solo se informan conteos por regla. Las llamadas se registran en `services/api/audit.log` (ignorado por Git), sin contenido del CSV.

## Resultado esperado con el fichero de prueba

100 registros: 94 válidos y 6 inválidos (1 por regla); satisfacción media 3.58.