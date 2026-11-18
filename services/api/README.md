# API de HealthCore

Backend FastAPI del monorepo. La API y el script `scripts/analyze.py` usan la misma lógica en `src/api/incidents/analysis.py`.

## Requisitos

- Python 3.14 o posterior, según `pyproject.toml`

## Instalación y arranque desde cero

Desde la raíz del repositorio:

```bash
cd services/api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m uvicorn api.main:app --app-dir src --reload --host 127.0.0.1 --port 8000
```

La API queda disponible en `http://127.0.0.1:8000`; la documentación interactiva está en `http://127.0.0.1:8000/docs`. Para usarla desde `uis/backoffice`, inicia también el frontend en el puerto 3000. Su rewrite reenvía `/api/*` a la API.

## Autenticación y auditoría

- `POST /auth/login` (formulario `username`/`password`) devuelve un token JWT Bearer. Requiere `SECRET_KEY` en `.env`.
- Los endpoints de incidencias y `/records/*` exigen `Authorization: Bearer <token>`; sin token o con token inválido responden 401.
- Cada login y cada uso de incidencias se registra en `services/api/audit.log` (una línea JSON por evento: fecha, acción, resultado, id de usuario, IP y ruta). No se registran contraseñas, tokens ni contenido de los CSV. El fichero está en `.gitignore`.

## Endpoints de incidencias

Requieren token Bearer.

- `POST /api/incidents/analyze`: recibe `file` como `multipart/form-data` y devuelve el resumen JSON.
- `GET /api/incidents/results/export`: descarga `resultados_healthcore.csv` con métricas agregadas del último análisis correcto del proceso.

Ejemplo de prueba local (primero obtén el token con un usuario existente):

```bash
TOKEN=$(curl -s -d "username=usuario@ejemplo.com&password=TU_CONTRASENA" http://127.0.0.1:8000/auth/login | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -H "Authorization: Bearer $TOKEN" -F "file=@../../scripts/incidents-HEALTHCORE.csv" http://127.0.0.1:8000/api/incidents/analyze
curl -OJ -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/incidents/results/export
```

Para analizar el CSV de 100 filas desde la línea de comandos, ejecuta desde la raíz del repositorio `scripts/analizar-datos-prueba.sh`. Si respondes `s` al preguntar por la exportación, el resultado se guarda en `results.csv` en el directorio actual.

Los datos originales del fichero no se guardan ni se incluyen en el CSV exportado. Para el prototipo, el último resultado vive en memoria y se reinicia al reiniciar el proceso; ejecútalo con un único worker.

## Alcance y seguridad

`scripts/incidents-HEALTHCORE.csv` y `scripts/incidents-HEALTHCORE-datos-prueba.csv` contienen los mismos 100 registros de prueba. El briefing de HealthCore no define un catálogo de categorías ni valores esperados para incidencias; por ahora, las categorías válidas se toman de las cinco categorías presentes en los CSV. Confirma ese catálogo y los valores de referencia antes de usar datos de producción.

El acceso requiere autenticación JWT y queda auditado. Solo un `admin` puede crear usuarios (`POST /users`). Los roles `admin` y `user` acceden a incidencias y registros con cualquier token válido. El transporte cifrado (HTTPS) no está implementado. No hay aprobación de Cumplimiento registrada para datos reales ni para el despliegue. Mantén el backend ligado a `127.0.0.1` y no proceses datos reales sensibles.
