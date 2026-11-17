# .agents/ — Configuración de Agentes de Desarrollo

Esta carpeta contiene las **reglas y skills** que configuran cómo operan los agentes de código (Copilot, Cursor, Claude) cuando trabajan en este repositorio de HealthCore.

> **⚠️ No confundas esto con `/agents/` y `/skills/`:** Estos últimos son **código de producto** que construirás (agentes de IA que resuelven problemas de negocio). Esta carpeta `.agents/` es **configuración de desarrollo** — le enseña al agente cómo trabajar sin romper lo que ya existe.

---

## Estructura

```
.agents/
├── README.md                    # Este archivo
├── /rules/                      # Reglas que el agente debe seguir SIEMPRE
│   ├── compliance-and-data-access.md   # HIPAA, GDPR, secrets
│   └── folder-structure.md              # Dónde va cada código
└── /skills/                     # Skills reutilizables (tarea recurrente)
    └── validate-precommit.md    # Validar sintaxis, secrets, docs antes de commit
```

---

## Reglas (`.agents/rules/`)

Las **reglas** son protocolos obligatorios que el agente respeta automáticamente. Cada regla especifica:
- **Alcance:** Cuándo aplica (siempre, por patrón, etc.)
- **Objetivo:** Qué problema resuelve
- **Criterios de aceptación:** Cómo verificar que se cumple

### Reglas Actuales

| Regla | Alcance | Qué Protege |
|-------|---------|------------|
| [`compliance-and-data-access.md`](./rules/compliance-and-data-access.md) | **Siempre activa** | Datos de pacientes, HIPAA/GDPR, secrets |
| [`folder-structure.md`](./rules/folder-structure.md) | **Siempre activa** | Ubicación correcta del código, sin carpetas paralelas |

---

## Skills (`.agents/skills/`)

Las **skills** son instrucciones estructuradas para una **tarea recurrente** del flujo de trabajo. Cada skill:
- Tiene **un objetivo único**
- Define **inputs esperados**
- Especifica **criterios de aceptación verificables**
- Puede **testearse de forma independiente**

### Skills Actuales

| Skill | Objetivo | Cuándo Usarla |
|-------|----------|---------------|
| [`validate-precommit.md`](./skills/validate-precommit.md) | Validar sintaxis, secrets, carpetas y documentación antes de commit | Paso 1 de AGENTS.md, antes de hacer `git commit` |

---

## Cómo Funciona

### 1. Al Iniciar Sesión
El agente lee:
1. `memory-bank/projectbrief.md` — Qué es HealthCore
2. `memory-bank/techContext.md` — Arquitectura técnica
3. `memory-bank/progress.md` — Estado actual

Luego revisita `.agents/rules/` para entender qué **NO** puede hacer.

### 2. Cuando Escribe Código
El agente respeta:
- **`compliance-and-data-access.md`** → No hardcodea secrets, registra auditoría
- **`folder-structure.md`** → Pone código en carpeta correcta

### 3. Antes de Hacer Commit
El agente ejecuta la skill **`validate-precommit.md`**:
- ✓ Verifica sintaxis
- ✓ Busca secrets
- ✓ Valida carpetas
- ✓ Revisa que `progress.md` se actualizó

Si pasa → continúa. Si falla → detiene y reporta qué corregir.

---

## Agregar Nuevas Reglas

Si necesitas que el agente respete una **nueva restricción o protocolo:**

1. Crea archivo `<rule-name>.md` en `.agents/rules/`
2. Incluye:
   - **Alcance de Aplicación** (siempre, por patrón, por demanda, etc.)
   - **Objetivo** (qué problema resuelve)
   - **Restricciones Obligatorias** (qué está prohibido)
   - **Criterios de Aceptación** (✅ pasa si / ❌ bloquea si)
3. Referencia la regla en `AGENTS.md` o `memory-bank/techContext.md`

**Ejemplo:**
```markdown
# Regla: Usar TypeScript en APIs

## Alcance
Por patrón: archivos en `/services/**/*.js` creados después de 2026-11-20

## Objetivo
Mejorar type-safety en APIs que acceden a datos sensibles

## Restricciones
- Todos los archivos nuevos en `/services` deben ser `.ts`
- Usar interfaces explícitas para entrada/salida de datos
```

---

## Agregar Nuevas Skills

Si hay una **tarea recurrente** que el agente puede automatizar:

1. Crea archivo `SKILL.md` en `.agents/skills/<skill-name>/`
2. Incluye:
   - **Resumen** (qué hace)
   - **Objetivo Único** (una sola cosa)
   - **Inputs** (qué recibe, en tabla o código)
   - **Proceso de Ejecución** (pasos, fases, scripts)
   - **Output Esperado** (resultado éxito y fracaso)
   - **Criterios de Aceptación** (✅ / ❌)
   - **Implementación** (pseudocódigo o script real)
   - **Cuándo Usar** (cuál es el trigger)
3. Integra con `AGENTS.md` indicando en qué paso se ejecuta

**Ejemplo:**
```markdown
# SKILL: Generar changelog automático

## Objetivo Único
Generar sección de changelog basada en commits desde último release

## Inputs
- `commits_since`: Commits desde último tag
- `version`: Versión nueva

## Proceso
1. Leer todos los commits
2. Agrupar por categoría (features, fixes, docs)
3. Generar markdown
4. Insertar en CHANGELOG.md

## Criterios de Aceptación
✅ Si CHANGELOG.md fue actualizado
✅ Si tiene secciones para cada categoría
❌ Si falta versión o fecha
```

---

## Referencias

- **`AGENTS.md`** — Flujo obligatorio de desarrollo
- **`memory-bank/`** — Contexto de negocio y técnico
- **`README.md` de carpetas** — Instrucciones sobre `/uis/website`, `/uis/backoffice`, `/services`

---

## Versión
- **v1.0** — 2026-11-17
- Inicial: 2 reglas (compliance, folder structure) + 1 skill (validate-precommit)
