# SKILL: Validar Cambios Pre-Commit

## Resumen
Skill que automatiza la verificación de código y documentación antes de que el agente haga un commit, asegurando que los cambios cumplen con estándares de HealthCore (sintaxis, compliance, documentación).

---

## Objetivo Único
**Garantizar que ningún commit se haga sin antes verificar:**
1. ✓ No hay errores de sintaxis
2. ✓ No hay datos sensibles o secrets en el código
3. ✓ La documentación (progress.md) se actualizó
4. ✓ Se respetan reglas de carpetas y compliance

---

## Inputs (Qué recibe la skill)

| Input | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `files_changed` | array | Lista de archivos modificados | `["src/api/patients.js", "memory-bank/progress.md"]` |
| `branch_name` | string | Nombre de la rama actual | `"feature/agent-memory-bank"` |
| `commit_message` | string | Mensaje de commit propuesto | `"Add patient API endpoint"` |

**Cómo obtener inputs:**
```bash
# Archivo modificado
git diff --name-only

# Rama actual
git branch --show-current

# Mensaje propuesto
# (el agente lo define en AGENTS.md paso 4)
```

---

## Proceso de Validación

### Fase 1: Validación de Sintaxis
```bash
# Para archivos JavaScript/Node.js
node -c <archivo>

# Para JSON
jq empty <archivo>
```

**Criterio:** ✅ Pasa si no hay errores de compilación

---

### Fase 2: Verificación de Secrets (Compliance)
```bash
# Buscar patrones peligrosos
grep -r "password\|token\|SECRET\|API_KEY\|private_key" <archivos> \
  --exclude-dir=node_modules \
  --exclude="*.env" \
  --exclude=".env*"

# Buscar valores hardcodeados
grep -r "const.*=.*['\"].*@.*\.com['\"]" <archivos>  # emails
grep -r "const.*=.*['\"][0-9]\{6,\}['\"]" <archivos>  # números largos
```

**Criterio:** ✅ Pasa si NO encuentra matches (cero secrets)

---

### Fase 3: Validación de Reglas de Carpetas
Verifica que archivos nuevos están en la ubicación correcta.

```bash
# Detectar si hay archivos en carpetas prohibidas
find . -type d \( -name "my-app" -o -name "new-frontend" -o -name "custom-backend" \) \
  -not -path "./.git/*"
```

**Criterio:** ✅ Pasa si NO existen carpetas paralelas

---

### Fase 4: Validación de Documentación
Verifica que `memory-bank/progress.md` se actualizó.

```bash
# Verificar que progress.md fue modificado
git diff --name-only | grep -q "memory-bank/progress.md"

# Verificar que tiene contenido (no está vacío ni tiene solo placeholders)
grep -v "^\[" memory-bank/progress.md | grep -v "^$" | wc -l
```

**Criterio:** ✅ Pasa si:
- progress.md fue modificado en este commit
- Contiene texto real (no solo placeholders)
- Fecha es actual (no dice "[Pon la fecha de hoy...]")

---

### Fase 5: Validación de Compliance (si aplica)
Si los archivos modificados tocan datos sensibles (`/services/api/patients`, `/uis/backoffice`):

```bash
# Buscar funciones que acceden a datos sin auditoría
grep -n "db\\.patients\|SELECT.*FROM.*patients" <archivos> | \
  grep -v "auditLog\|audit\|log"
```

**Criterio:** ✅ Pasa si acceso a datos tiene registro de auditoría

---

## Output Esperado

### Escenario 1: ✅ Validación Exitosa
```
✅ PRE-COMMIT VALIDATION PASSED

Fase 1: Sintaxis         ✓ OK
Fase 2: No Secrets       ✓ OK (0 potenciales secrets encontrados)
Fase 3: Carpetas         ✓ OK (estructura correcta)
Fase 4: Documentación    ✓ OK (progress.md actualizado)
Fase 5: Compliance       ✓ OK (auditoría presente)

👍 Listo para commit
Mensaje propuesto: "Add patient API endpoint"
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

### Escenario 2: ❌ Validación Fallida
```
❌ PRE-COMMIT VALIDATION FAILED

Fase 1: Sintaxis         ✗ ERROR en src/api/patients.js:45
                           SyntaxError: Unexpected token }

Fase 2: No Secrets       ✗ WARNING en services/config/db.js:12
                           Posible password hardcodeado encontrado

Fase 3: Carpetas         ✓ OK
Fase 4: Documentación    ✗ ERROR memory-bank/progress.md no fue modificado

Resultado: 🛑 BLOQUEADO PARA COMMIT
Acciones necesarias:
  1. Corregir errores de sintaxis en src/api/patients.js
  2. Mover secretos a .env en services/config/db.js
  3. Actualizar memory-bank/progress.md con resumen de cambios

Contactar al desarrollador para resolver bloqueos.
```

---

## Criterios de Aceptación

✅ La skill PASA si:
1. ✓ No hay errores de sintaxis en ningún archivo
2. ✓ No hay passwords, tokens o secretos hardcodeados
3. ✓ No hay carpetas nuevas fuera de estructura
4. ✓ `memory-bank/progress.md` fue actualizado con cambios reales
5. ✓ Si se toca código de pacientes, hay auditoría registrada

❌ La skill FALLA si:
1. ✗ Hay syntax errors en JavaScript, JSON, etc.
2. ✗ Se encuentra cualquier secret o credential
3. ✗ Se creó una carpeta nueva no autorizada
4. ✗ `progress.md` no se actualizó o está vacío
5. ✗ Acceso a datos sensibles sin auditoría

---

## Implementación (Pseudocódigo para el Agente)

```javascript
// Archivo: .agents/skills/validate-precommit.js
// Ejecutado ANTES de hacer git commit

async function validatePreCommit() {
  const filesChanged = execSync('git diff --name-only').toString().split('\n');
  const branch = execSync('git branch --show-current').toString().trim();
  
  let results = {
    syntaxOk: true,
    noSecrets: true,
    folderStructureOk: true,
    progressUpdated: true,
    complianceOk: true,
    errors: []
  };

  // Fase 1: Sintaxis
  for (const file of filesChanged) {
    if (file.endsWith('.js')) {
      try {
        require(file);  // Simple syntax check
      } catch (e) {
        results.syntaxOk = false;
        results.errors.push(`Syntax error in ${file}: ${e.message}`);
      }
    }
  }

  // Fase 2: Secrets
  const secretPatterns = [
    /password\s*=|TOKEN\s*=|SECRET\s*=/i,
    /private_key|api_key/i
  ];
  for (const file of filesChanged) {
    const content = readFileSync(file, 'utf8');
    for (const pattern of secretPatterns) {
      if (pattern.test(content)) {
        results.noSecrets = false;
        results.errors.push(`Potential secret in ${file}`);
      }
    }
  }

  // Fase 3: Folders
  if (!branch.startsWith('feature/')) {
    results.errors.push(`Branch name must start with 'feature/'`);
  }

  // Fase 4: Progress Updated
  if (!filesChanged.includes('memory-bank/progress.md')) {
    results.progressUpdated = false;
    results.errors.push(`memory-bank/progress.md was not updated`);
  }

  // Return validation results
  return results;
}
```

---

## Cuándo Usar Esta Skill

**El agente ejecuta esta skill:**
- ✅ Justo antes de hacer `git commit`
- ✅ Como parte del Paso 1 de AGENTS.md ("Revisar que el código no tenga errores")
- ✅ Cada vez que modifica código

**Resultado:**
- Si ✅ pasa: continúa con Paso 2 de AGENTS.md (actualizar progress.md)
- Si ❌ falla: detiene el flujo y reporta qué corregir

---

## Referencias

- **AGENTS.md** → Paso 1 y 2 del flujo de commit
- **`.agents/rules/compliance-and-data-access.md`** → Qué es "acceso a datos sin auditoría"
- **`.agents/rules/folder-structure.md`** → Validación de carpetas
- **`memory-bank/progress.md`** → Debe actualizarse en cada sesión

---

## Versión
- **v1.0** — 2026-11-17
- Validación de sintaxis, secrets, carpetas, documentación y compliance básico
