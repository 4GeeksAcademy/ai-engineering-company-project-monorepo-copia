# Regla: Estructura de Carpetas y Ubicación de Código

## Alcance de Aplicación
**Siempre activa** — se aplica cuando el agente crea nuevos archivos o módulos.

## Objetivo
Mantener una estructura clara y predecible en el monorepo para que todos los sistemas de HealthCore (web pública, panel interno, APIs) coexistan sin colisiones.

## Mapa de Ubicaciones

### `/uis/website` — Web Pública de HealthCore
Interfaz cara al paciente. Lo ven los pacientes cuando acceden a reservar citas.
- **Responsabilidad:** Información de la empresa, reservas de citas, estado de citas
- **Stack:** HTML, CSS, JavaScript
- **Contenido:** Branding de HealthCore, horarios, cómo reservar
- **Dato sensible:** Nombre del paciente, teléfono (controlado con GDPR/HIPAA)

**Permitido:**
```
/uis/website/
  index.html
  css/
  js/
  assets/
  components/
```

**❌ No permitido:** Código de lógica médica, cálculos de facturación, decisiones clínicas

---

### `/uis/backoffice` — Panel Interno de HealthCore
Interfaz para médicos, enfermeras, personal administrativo y ejecutivos.
- **Responsabilidad:** Dashboard de citas, historias clínicas (acceso controlado), facturación, reportes
- **Stack:** HTML, CSS, JavaScript (con autenticación requerida)
- **Contenido:** Vistas de pacientes, gestión de citas, reportes operacionales
- **Dato sensible:** Historias clínicas completas (máxima restricción HIPAA/GDPR)

**Permitido:**
```
/uis/backoffice/
  index.html
  components/
    patient-dashboard.js
    billing-dashboard.js
    operations-dashboard.js
  css/
  assets/
```

**❌ No permitido:** Datos públicos (esos van a `/uis/website`), lógica de backend pura

---

### `/services` — APIs y Lógica Backend
Backend que alimenta tanto website como backoffice.
- **Responsabilidad:** Autenticación, acceso a datos, cálculos, integración con EHR
- **Stack:** Node.js, Express (o similar)
- **Contenido:** Endpoints, validación, queries a BD, lógica de negocio

**Permitido:**
```
/services/
  api/
    auth.js              # Login, tokens
    patients.js          # Leer/escribir historias (con permisos)
    appointments.js      # Gestionar citas
    billing.js           # Lógica de facturación
    compliance.js        # Auditoría y logs
  middleware/
    authenticate.js      # Verificar token
    authorize.js         # Verificar permisos
    auditLog.js          # Registrar acciones
  models/
    patient.js
    appointment.js
  config/
    db.js
```

**❌ No permitido:** Código de UI/CSS, archivos HTML puros

---

## Reglas Prácticas

### 1. ¿Dónde va este código?

| Pregunta | Respuesta | Ubicación |
|----------|-----------|-----------|
| ¿Es una página que ven los pacientes? | Sí → | `/uis/website` |
| ¿Es una página solo para staff interno? | Sí → | `/uis/backoffice` |
| ¿Es lógica que varios frontends necesitan? | Sí → | `/services` |
| ¿Es un cálculo de negocio (ej: rechazo de factura)? | Sí → | `/services` |
| ¿Accede directamente a BD? | Sí → | `/services` |

### 2. No hagas carpetas paralelas
❌ **NO HAGAS:**
```
/my-custom-app/
/new-frontend/
/another-backend/
/utils-compartidos/
```

✅ **SÍ HACES:**
Reutiliza las carpetas existentes o expande dentro de ellas.

### 3. Si necesitas código compartido
Usa `/shared/` para utilidades reutilizables:
```
/shared/
  helpers/
  constants/
  types/
```

Luego importa desde cualquier lugar:
```javascript
// En /uis/website/js/index.js
import { formatDate } from '../../../shared/helpers';

// En /services/api/appointments.js
import { validateEmail } from '../../shared/helpers';
```

---

## Criterios de Aceptación

✅ Pasa si:
1. ✓ Código está en la carpeta correcta según su responsabilidad
2. ✓ No hay carpetas nuevas creadas fuera de la estructura permitida
3. ✓ Si es código compartido, va en `/shared/`
4. ✓ Estructura es predecible para otros desarrolladores

❌ Bloquea el commit si:
1. ✗ Se creó una carpeta nueva no documentada (ej: `/apps/`, `/modules/`)
2. ✗ Código está en la carpeta equivocada (ej: lógica de BD en `/uis/website`)
3. ✗ Hay duplicación de código en múltiples carpetas

## Checklist para el Agente

Antes de crear un archivo nuevo, pregúntate:
- [ ] ¿Qué responsabilidad tiene? (UI, backend, compartido)
- [ ] ¿En cuál de las 3 carpetas (`/uis/website`, `/uis/backoffice`, `/services`) encaja?
- [ ] ¿Otros equipos necesitarán este código? → `/shared/`
- [ ] ¿Es código duplicado? → Refactorizar a `/shared/`

## Referencias
- `memory-bank/techContext.md` — Especifica la estructura
- `AGENTS.md` → Sección 3: "Dónde va el código"
