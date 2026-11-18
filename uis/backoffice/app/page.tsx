"use client";

import { FormEvent, useState } from "react";

type AnalysisResult = {
  total_processed: number;
  valid_records: number;
  invalid_records: number;
  invalid_by_reason: Record<string, number>;
  invalid_record_details: { row_number: number; reasons: string[] }[];
  categories: Record<string, number>;
  states: Record<string, number>;
  closed_case_satisfaction_avg: number | null;
};

const formatNumber = new Intl.NumberFormat("es-ES");

function formatReason(reason: string): string {
  if (reason.startsWith("missing_field:")) {
    const field = reason.split(":")[1];
    const fieldLabels: Record<string, string> = {
      id_incidencia: "ID de incidencia",
      departamento: "departamento",
      categoria: "categoría",
      estado: "estado",
    };
    return `Falta el campo ${fieldLabels[field] ?? field}`;
  }
  if (reason === "invalid_category") return "Categoría fuera del catálogo";
  if (reason === "invalid_state") return "Estado fuera del catálogo";
  if (reason === "malformed_row") return "Fila con columnas adicionales";
  return reason;
}

function Breakdown({
  title,
  values,
  emptyLabel,
}: {
  title: string;
  values: Record<string, number>;
  emptyLabel: string;
}) {
  const entries = Object.entries(values);

  return (
    <section className="breakdown-section">
      <div className="section-heading">
        <h2>{title}</h2>
        <span>{formatNumber.format(entries.length)} grupos</span>
      </div>
      {entries.length === 0 ? (
        <p className="empty-breakdown">{emptyLabel}</p>
      ) : (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th scope="col">Nombre</th>
                <th scope="col">Incidencias</th>
              </tr>
            </thead>
            <tbody>
              {entries.map(([label, count]) => (
                <tr key={label}>
                  <td>{label}</td>
                  <td>{formatNumber.format(count)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default function IncidentsPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoginError("");
    setIsLoggingIn(true);
    try {
      const response = await fetch("/auth/login", {
        method: "POST",
        body: new URLSearchParams({ username: email, password }),
      });
      if (!response.ok) {
        throw new Error("Email o contraseña incorrectos.");
      }
      const payload = await response.json();
      setToken(payload.access_token as string);
      setPassword("");
    } catch (requestError) {
      setLoginError(
        requestError instanceof Error ? requestError.message : "No se pudo iniciar sesión.",
      );
    } finally {
      setIsLoggingIn(false);
    }
  }

  async function handleExport() {
    const response = await fetch("/api/incidents/results/export", {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (response.status === 401) {
      setLoginError("Tu sesión ha caducado. Vuelve a iniciar sesión.");
      setToken("");
      return;
    }
    if (!response.ok) {
      setError("No se pudo exportar el resultado.");
      return;
    }
    const url = URL.createObjectURL(await response.blob());
    const link = document.createElement("a");
    link.href = url;
    link.download = "resultados_healthcore.csv";
    link.click();
    URL.revokeObjectURL(url);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("Selecciona un fichero CSV para continuar.");
      return;
    }

    setError("");
    setIsSubmitting(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/incidents/analyze", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      if (response.status === 401) {
        setLoginError("Tu sesión ha caducado. Vuelve a iniciar sesión.");
        setToken("");
        return;
      }
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail ?? "No se pudo analizar el fichero.");
      }
      setResult(payload as AnalysisResult);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "No se pudo conectar con el servicio de análisis.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  if (!token) {
    return (
      <main className="workspace">
        <section className="page-heading" aria-labelledby="login-title">
          <p className="eyebrow">ACCESO RESTRINGIDO <span>/</span> HEALTHCORE</p>
          <h1 id="login-title">Iniciar sesión</h1>
        </section>
        <form className="upload-panel" onSubmit={handleLogin}>
          <label htmlFor="login-email">Email</label>
          <input
            id="login-email"
            type="email"
            autoComplete="username"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
          <label htmlFor="login-password">Contraseña</label>
          <input
            id="login-password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
          <button className="primary-button" type="submit" disabled={isLoggingIn}>
            {isLoggingIn ? "Entrando…" : "Entrar"}
          </button>
          {loginError && <p className="error-message" role="alert">{loginError}</p>}
        </form>
      </main>
    );
  }

  return (
    <main className="workspace">
      <header className="topbar">
        <a className="brand" href="/" aria-label="HealthCore, inicio">
          <span className="brand-mark" aria-hidden="true">H</span>
          <span>HealthCore<span className="brand-divider">/</span>Digital</span>
        </a>
        <div className="topbar-context">
          <span className="status-dot" aria-hidden="true" />
          OPERACIONES INTERNAS
          <button type="button" onClick={() => { setToken(""); setResult(null); }}>
            Cerrar sesión
          </button>
        </div>
      </header>

      <section className="page-heading" aria-labelledby="page-title">
        <p className="eyebrow">DATOS Y CALIDAD <span>/</span> HEALTHCORE</p>
        <div className="heading-row">
          <div>
            <h1 id="page-title">Análisis de incidencias</h1>
            <p className="page-description">
              Validación y resumen de registros operativos, procesados dentro de HealthCore.
            </p>
          </div>
          <span className="privacy-tag"><span aria-hidden="true">●</span> Procesamiento interno</span>
        </div>
      </section>

      <div className="content-grid">
        <aside className="upload-panel" aria-labelledby="upload-title">
          <div className="panel-kicker"><span>01</span> NUEVO ANÁLISIS</div>
          <h2 id="upload-title">Cargar fichero</h2>
          <p className="upload-copy">
            El CSV se analiza en el servicio interno. Los resultados exportables contienen métricas agregadas.
          </p>
          <form onSubmit={handleSubmit}>
            <label className="file-picker" htmlFor="incident-file">
              <span className="file-glyph" aria-hidden="true">＋</span>
              <span className="file-picker-copy">
                <strong>{file ? file.name : "Seleccionar fichero CSV"}</strong>
                <small>{file ? `${(file.size / 1024).toFixed(1)} KB` : "CSV · UTF-8"}</small>
              </span>
              <span className="browse-label">Examinar</span>
            </label>
            <input
              id="incident-file"
              className="file-input"
              type="file"
              accept=".csv,text/csv"
              onChange={(event) => {
                const nextFile = event.target.files?.[0] ?? null;
                setFile(nextFile);
                setError("");
              }}
            />
            <button className="primary-button" type="submit" disabled={isSubmitting || !file}>
              {isSubmitting ? "Analizando…" : "Analizar fichero"}
              <span aria-hidden="true">→</span>
            </button>
          </form>
          {error && <p className="error-message" role="alert">{error}</p>}
          <div className="privacy-note">
            <span className="privacy-icon" aria-hidden="true">i</span>
            <p>Los registros inválidos se contabilizan y se excluyen de los agregados.</p>
          </div>
        </aside>

        <section className="results" aria-live="polite" aria-busy={isSubmitting}>
          {result ? (
            <>
              <div className="results-header">
                <div>
                  <div className="panel-kicker"><span>02</span> RESUMEN DEL ANÁLISIS</div>
                  <h2>Resultados</h2>
                </div>
                <button className="export-link" type="button" onClick={handleExport}>
                  <span aria-hidden="true">↓</span> Exportar CSV
                </button>
              </div>

              <div className="metric-grid">
                <article className="metric metric-dark">
                  <span>PROCESADOS</span>
                  <strong>{formatNumber.format(result.total_processed)}</strong>
                  <small>Registros leídos</small>
                </article>
                <article className="metric">
                  <span>VÁLIDOS</span>
                  <strong>{formatNumber.format(result.valid_records)}</strong>
                  <small>Incluidos en métricas</small>
                </article>
                <article className={`metric ${result.invalid_records > 0 ? "metric-alert" : ""}`}>
                  <span>INVÁLIDOS</span>
                  <strong>{formatNumber.format(result.invalid_records)}</strong>
                  <small>Excluidos del análisis</small>
                </article>
                <article className="metric">
                  <span>SATISFACCIÓN</span>
                  <strong>{result.closed_case_satisfaction_avg === null ? "—" : result.closed_case_satisfaction_avg.toFixed(2)}</strong>
                  <small>Media en casos cerrados · / 5</small>
                </article>
              </div>

              {result.invalid_records > 0 && (
                <section className="validation-report" aria-labelledby="invalid-title">
                  <div className="validation-header">
                    <div>
                      <p className="panel-kicker">VALIDACIÓN</p>
                      <h3 id="invalid-title">Registros que requieren revisión</h3>
                    </div>
                    <strong>{formatNumber.format(result.invalid_records)}</strong>
                  </div>
                  <ul className="reason-list">
                    {Object.entries(result.invalid_by_reason).map(([reason, count]) => (
                      <li key={reason}><span>{formatReason(reason)}</span><strong>{count}</strong></li>
                    ))}
                  </ul>
                  <p className="row-list-label">Filas del fichero</p>
                  <p className="row-list">
                    {result.invalid_record_details.map((record) => `#${record.row_number}`).join(" · ")}
                  </p>
                </section>
              )}

              <div className="breakdown-grid">
                <Breakdown title="Por categoría" values={result.categories} emptyLabel="Sin categorías válidas." />
                <Breakdown title="Por estado" values={result.states} emptyLabel="Sin estados válidos." />
              </div>
            </>
          ) : (
            <div className="empty-state">
              <div className="empty-mark" aria-hidden="true">∑</div>
              <p className="panel-kicker">ESPERANDO DATOS</p>
              <h2>El resumen aparecerá aquí</h2>
              <p>Selecciona un CSV de incidencias y ejecuta el análisis para ver sus métricas.</p>
            </div>
          )}
        </section>
      </div>
      <footer className="page-footer">
        <span>HEALTHCORE DIGITAL</span>
        <span>Acceso restringido · Datos operativos</span>
      </footer>
    </main>
  );
}
