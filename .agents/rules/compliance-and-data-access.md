# Regla: Cumplimiento de Datos y Acceso (Compliance and Data Access)

## Alcance de Aplicación
**Siempre activa** — se aplica a TODOS los cambios de código que toquen datos de pacientes, autenticación, o información sensible.

## Objetivo
Garantizar que cualquier código que el agente escriba respete HIPAA (EE.UU.) y UK GDPR (Reino Unido) y no introduzca vulnerabilidades de acceso a datos.

## Restricciones Obligatorias

### 1. Nunca hardcodear datos sensibles
- ❌ **NO:** Credenciales, tokens, o datos de pacientes en el código
- ✅ **SÍ:** Usar variables de entorno en `.env` (nunca en git)

**Verificación:**
```bash
grep -r "password\|token\|SECRET\|patient\|ssn" <archivo> | grep -v ".env"
```

### 2. Acceso a datos de pacientes
Cualquier API o función que lea datos de pacientes debe:
- Registrar la acción en un log de auditoría (quién accedió, cuándo, qué datos)
- Verificar que el usuario tiene permiso (autenticación + autorización)
- Nunca exponer ID internos en respuestas públicas

**Patrón recomendado:**
```javascript
// En /services/api/patient-data
async function getPatientRecord(patientId, userId, userRole) {
  // 1. Verificar que el usuario tiene permiso
  if (!hasAccessToPatient(userId, patientId, userRole)) {
    throw new UnauthorizedError("Access denied");
  }
  // 2. Registrar en auditoría
  await auditLog.record({
    action: "PATIENT_DATA_ACCESSED",
    patientId,
    userId,
    timestamp: new Date(),
  });
  // 3. Retornar datos
  return db.patients.findById(patientId);
}
```

### 3. Dos sistemas EHR, dos responsabilidades
HealthCore tiene:
- Sistema EHR para clínicas en EE.UU. (HIPAA)
- Sistema EHR para clínicas en Reino Unido (UK GDPR)

Si el código accede a ambos sistemas:
- Documentar explícitamente cuál es el cumplimiento esperado en cada país
- Testear ambas rutas (US y UK) si es posible
- Incluir comentario: `// EHR: US HIPAA` o `// EHR: UK GDPR`

### 4. No procesamiento de datos en cliente (browser)
- ❌ **NO:** Dejar datos de pacientes en JavaScript del lado del cliente
- ✅ **SÍ:** Procesar en backend (`/services`) y enviar solo lo que el usuario necesita ver

## Criterios de Aceptación

✅ Pasa si:
1. ✓ No hay credenciales o secretos en el código fuente
2. ✓ Todo acceso a datos de pacientes está autenticado
3. ✓ Existe log de auditoría para operaciones sensibles
4. ✓ Código claramente marcado por jurisdicción (US/UK)
5. ✓ No hay datos sensibles en respuestas públicas

❌ Bloquea el commit si:
1. ✗ Contiene contraseñas, tokens o secrets en el código
2. ✗ Acceso a datos sin autenticación verificada
3. ✗ No hay registro de auditoría para operaciones críticas
4. ✗ Usa datos de pacientes en JavaScript del cliente

## Referencia
- [HIPAA Compliance Checklist](https://www.hhs.gov/hipaa/)
- [UK GDPR Data Processing](https://ico.org.uk/for-organisations/data-protection/)
- Ver también: `memory-bank/projectbrief.md` (HealthCore opera bajo dos marcos legales)
