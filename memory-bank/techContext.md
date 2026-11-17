# Tech Context: HealthCore Digital

## ¿Quiénes somos en Tecnología?

HealthCore Digital es la unidad interna responsable de construir, mantener e integrar todos los sistemas que permiten a HealthCore operar como una red sanitaria moderna, segura y centrada en el paciente. Reportamos a la **Dra. Sandra Okonkwo** (CEO) y trabajamos bajo la dirección de **James Osei** (CTO, Austin).

---

## La Infraestructura Actual (El Desafío)

HealthCore opera un mosaico de sistemas heredados que nunca se integraron correctamente:

| Sistema | Ubicación | Problema |
|---------|-----------|----------|
| **EHR (Historias Clínicas)** | EE.UU. | Plataforma A — solo US |
| **EHR (Historias Clínicas)** | UK | Plataforma B — no comunica con US |
| **Programación de Citas** | EE.UU. | Sistema por teléfono, sin API |
| **Programación de Citas** | UK | Agenda manual, sin digitalizar |
| **Facturación** | EE.UU. | Plataforma dedicada |
| **Facturación** | UK | Hoja de cálculo manual |
| **Gestión de RRHH** | Ambos | Hoja de cálculo + emails |

**Resultado:** No hay una capa de datos compartida. No hay telemetría. No hay integración.

---

## Nuestra Estructura de Monorepo

Este repositorio centraliza TODA la tecnología de HealthCore en un mismo lugar:

```
healthcore-monorepo/
├── /uis/                      # Interfaces de usuario
│   ├── /website               # 👥 Sitio público (pacientes)
│   │                           # Reservas, estado de citas, info de empresa
│   │                           # Responsable: Equipo de Experiencia del Paciente (Priya Nair)
│   │
│   └── /backoffice            # 🏥 Panel interno (staff + ejecutivos)
│                               # Dashboards clínicos, gestión de citas, facturación, reportes
│                               # Responsable: Equipo de Operaciones (Dr. Marcus Reid) + TI
│
├── /services/                 # 🔌 APIs y Backend
│   │                           # Autenticación, datos de pacientes, cálculos de negocio
│   │                           # Integración con ambos sistemas EHR
│   │                           # Responsable: Equipo de Tecnología (James Osei, CTO)
│   │
│   ├── /api/patients          # Lectura/escritura de historias clínicas (con permisos)
│   ├── /api/appointments      # Gestión de citas (reservas, recordatorios)
│   ├── /api/billing           # Lógica de facturación y detección de rechazos
│   ├── /api/compliance        # Auditoría y registros de acceso (HIPAA/GDPR)
│   └── /integrations          # Conectores a ambos sistemas EHR
│
├── /agents/                   # 🤖 Agentes de IA (HealthCore)
│   │                           # Cuando se creen: documentación asistida,
│   │                           # predicción de no-shows, análisis de rechazos, etc.
│   │
│   └── /skills                # Habilidades reutilizables de agentes
│
├── /memory-bank/              # 📚 Banco de memoria del agente
│   ├── projectbrief.md        # Qué es HealthCore, problemas a resolver
│   ├── techContext.md         # Esta arquitectura técnica
│   └── progress.md            # Estado del desarrollo, sesión a sesión
│
└── /.agents/                  # ⚙️ Reglas para agentes de DESARROLLO
    ├── /rules/                # Cómo codificar en este repo
    └── /skills/               # Skills reutilizables (validación precommit, etc.)
```

---

## Restricciones Técnicas y Legales

### HIPAA (EE.UU.)
- Aplica a: Clínicas en Texas, Florida y Georgia
- Requisito: Todos los datos de pacientes deben encriptarse en tránsito y en reposo
- Auditoría: Registrar QUIÉN accedió A QUÉ datos y CUÁNDO
- Acceso: Solo personal clínico autorizado puede ver historias

### UK GDPR (Reino Unido)
- Aplica a: Clínicas en Londres y Mánchester
- Requisito: Derecho del paciente a solicitar sus datos en cualquier momento
- Auditoría: Registrar todas las operaciones sobre datos personales
- Acceso: Personal autorizado solo, con consentimiento explícito del paciente

**En la práctica:** Cualquier código en `/services` que toque datos de pacientes DEBE:
1. Autenticar al usuario (verificar que es personal válido)
2. Autorizar la acción (verificar que tiene permiso en este paciente específico)
3. Auditar el acceso (guardar registro inmutable de quién vio qué)

---

## Departamentos y Sus Necesidades Técnicas

### 🏥 Operaciones Clínicas (Dr. Marcus Reid, 120 personas)
**Desafío:** Dos sistemas EHR desconectados, 35 minutos/día en documentación manual

**Lo que necesitan:**
- API unificada que exponga datos de ambos EHR (US + UK)
- Asistencia de IA para documentación clínica (reducir tiempo administrativo)
- Visibilidad del historial del paciente entre sedes
- Dashboard de operaciones: volumen de citas, flujo de pacientes, tiempo en documentación

---

### 🗓️ Experiencia del Paciente y Acceso (Priya Nair, Londres)
**Desafío:** Tasa de no-shows del 22% (1,8M dólares/año perdidos), sin reservas online

**Lo que necesitan:**
- Plataforma de reservas online unificada (EE.UU. + UK)
- Sistema de recordatorios: SMS/email/app previo a cita
- Modelo predictivo: marcar citas de alto riesgo de no-show
- Dashboard: tasas de reserva, no-shows, satisfacción por sede

---

### 💰 Ciclo de Ingresos y Facturación (Tom Callahan)
**Desafío:** Tasa de rechazo del 14% (doble de la media del sector), sin visión unificada

**Lo que necesitan:**
- Revisión asistida por IA: marcar reclamaciones de alto riesgo
- Sugerencias automáticas de códigos basadas en notas clínicas
- Dashboard de facturación unificado (EE.UU. + UK)
- Análisis de patrones: qué causas generan más rechazos

---

### 🔒 Cumplimiento y Datos (Claire Whitfield)
**Desafío:** Dos marcos legales (HIPAA + GDPR), pistas de auditoría fragmentadas

**Lo que necesitan:**
- Dashboard de cumplimiento centralizado (patrones de acceso, ambas jurisdicciones)
- Consolidación automática de auditoría en todos los EHR
- Automatización de solicitudes de datos de pacientes (HIPAA/GDPR)
- Sistema de puntuación de riesgo (alerta de posibles violaciones)

---

### 👥 Personas y RRHH (Diane Foster)
**Desafío:** 200 personas en 12 sedes, 2 países, 47 días promedio para cerrar perfil clínico

**Lo que necesitan:**
- Portal de RRHH: solicitudes de vacaciones, gestión de ausencias, consultas de políticas
- Onboarding clínico automatizado: verificación de credenciales, checklists
- Seguimiento de CME (educación médica continua): alertas de caducidad de licencias
- Dashboard de KPIs: tiempo de contratación, rotación, absentismo por sede

---

### 💻 Tecnología (James Osei, CTO, 6 personas)
**Desafío:** Mantener mosaico de sistemas heredados, sin telemetría, sin integración

**Lo que necesitan:**
- API central de HealthCore: unificar datos de pacientes, citas, facturación, personal
- Telemetría y monitorización en tiempo real desde 12 sedes
- Pipeline de datos: alimentar dashboards clínicos, operacionales, financieros
- Health checks automatizados con alertas cuando algo falla
- Documentación técnica indexada para búsqueda semántica

---

### 📊 Dirección Ejecutiva (Dra. Sandra Okonkwo, CEO)
**Desafío:** Gestiona 28M dólares en 2 países sin dashboard unificado

**Lo que necesita:**
- Dashboard ejecutivo: KPIs en tiempo real de todos los departamentos
- Informe semanal generado automáticamente (cada lunes a las 7am)
- Alertas de umbral: cuando métricas críticas se desvíen
- Asistente de IA: consultar en lenguaje natural ("¿Cuál es nuestra tasa de rechazo esta semana?")

---

## Decisiones Técnicas Tomadas

### 1. Monorepo vs. Microservicios
**Decisión:** Monorepo (todo en un repo)

**Por qué:** HealthCore tiene solo 6 personas en TI. Gestionar 5 repos separados sería overhead. Monorepo permite:
- Una sola versión de verdad
- Cambios coordinados entre UI y API
- CI/CD unificada

**Revisión en Q3 2027** si el equipo crece.

### 2. Stack Tecnológico
- **Frontend:** HTML, CSS, JavaScript (simple, mantenible)
- **Backend:** Node.js + Express (rápido de iterar, buen eco de librerías médicas)
- **BD:** PostgreSQL (soporte nativo para HIPAA, auditoría confiable)
- **Autenticación:** JWT tokens (stateless, seguro)
- **Auditoría:** Logs centralizados en PostgreSQL (trazabilidad completa)

### 3. Dos Geografías, Dos Sistemas EHR
**Decisión:** API unificada que abstrae ambos EHR

```
/services/api/patients  →  [Autenticación] → [Ruteo por país]
                                              ├→ USA EHR (HIPAA)
                                              └→ UK EHR (GDPR)
```

Así el frontend (`/uis/backoffice`, `/uis/website`) ve una API única, aunque bajo el capó hable con dos sistemas diferentes.

---

## Reglas Obligatorias

### ✅ Siempre Vigentes
1. **Nunca hardcodear secrets** — Usar `.env` (nunca en git)
2. **Acceso a pacientes requiere auditoría** — Registrar quién vio qué, cuándo
3. **Código va en carpetas correctas** — `/uis/website` para web pública, `/uis/backoffice` para panel interno, `/services` para backend
4. **Sin carpetas paralelas** — No inventar `/my-app`, `/new-frontend`, etc.
5. **Validar antes de commit** — Usar skill `validate-precommit.md`

Ver **`.agents/rules/`** para detalles.

---

## Flujo de Trabajo

1. **Leer:** `memory-bank/` al iniciar sesión
2. **Respetar:** Reglas en `.agents/rules/`
3. **Ejecutar:** Skills en `.agents/skills/` cuando corresponda
4. **Documentar:** Actualizar `memory-bank/progress.md` antes de commit
5. **Validar:** Correr `validate-precommit` antes de hacer commit
6. **Commit:** Incluir `Co-authored-by: Copilot` trailer

Ver **`AGENTS.md`** para flujo detallado.

---

## Próximos Pasos (Roadmap de Tecnología)

**Q4 2026 (Ahora):**
- ✅ Infraestructura de agentes documentada
- 🚀 API central de pacientes (integración con ambos EHR)
- 🚀 Dashboard ejecutivo básico

**Q1 2027:**
- Sistema de reservas online unificado
- Asistencia de IA para documentación clínica
- Predictor de no-shows

**Q2 2027:**
- Sistema de auditoría centralizado (HIPAA/GDPR)
- Portal de RRHH
- Análisis de patrones de rechazo

**Q3 2027:**
- Revisar si monorepo sigue siendo apropiado (si TI crece)
- Preparar para escala: caching, CDN, bases de datos replicadas

---

## Referencias

- **AGENTS.md** — Flujo de trabajo para agentes
- **`.agents/rules/compliance-and-data-access.md`** — Regla HIPAA/GDPR
- **`.agents/rules/folder-structure.md`** — Dónde va cada código
- **`.agents/skills/validate-precommit.md`** — Validación automática
- **`memory-bank/projectbrief.md`** — Contexto de negocio
