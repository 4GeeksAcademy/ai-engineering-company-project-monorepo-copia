"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

type Supplier = {
  id: number;
  name: string;
  country: "USA" | "UK";
  categories: string[];
  monthly_rate: number;
  currency: "USD" | "GBP";
  compliance_agreement: "BAA" | "DPA" | "both" | null;
  status: "active" | "suspended";
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const CATEGORIES = [
  "medical_supplies",
  "laboratory_services",
  "pharmaceutical",
  "clinical_software",
  "it_infrastructure",
  "hr_and_payroll_software",
  "cleaning_and_facilities",
  "patient_communication",
  "billing_and_coding_software",
  "training_platforms",
];

const categoryLabel = (category: string) =>
  category.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());

export default function Home() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [country, setCountry] = useState("");
  const [category, setCategory] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const loadSuppliers = useCallback(async () => {
    setError("");
    const params = new URLSearchParams();
    if (country) params.set("country", country);
    if (category) params.set("category", category);
    try {
      const response = await fetch(`${API_URL}/suppliers?${params.toString()}`);
      if (!response.ok) throw new Error(`La API respondió con HTTP ${response.status}`);
      setSuppliers(await response.json());
      setError("");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo conectar con la API.");
    }
  }, [country, category]);

  useEffect(() => {
    // Fetching synchronizes component state with the external API.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadSuppliers();
  }, [loadSuppliers]);

  const activeCount = useMemo(
    () => suppliers.filter((supplier) => supplier.status === "active").length,
    [suppliers],
  );

  async function updateSupplier(id: number, endpoint: "rate" | "status", body: object) {
    try {
      const response = await fetch(`${API_URL}/suppliers/${id}/${endpoint}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "No se pudo actualizar el proveedor.");
      await loadSuppliers();
    } catch (cause) {
      window.alert(cause instanceof Error ? cause.message : "Error de conexión con la API.");
    }
  }

  async function editRate(supplier: Supplier) {
    const value = window.prompt(`Nueva tarifa mensual para ${supplier.name}:`, String(supplier.monthly_rate));
    if (value === null) return;
    const monthly_rate = Number(value);
    if (!Number.isFinite(monthly_rate) || monthly_rate <= 0) {
      window.alert("Introduce una tarifa numérica mayor que cero.");
      return;
    }
    await updateSupplier(supplier.id, "rate", { monthly_rate });
  }

  async function toggleStatus(supplier: Supplier) {
    const status = supplier.status === "active" ? "suspended" : "active";
    await updateSupplier(supplier.id, "status", { status });
  }

  async function createSupplier(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    const selectedCountry = String(form.get("country"));
    const payload = {
      name: String(form.get("name")).trim(),
      country: selectedCountry,
      categories: [String(form.get("categories"))],
      monthly_rate: Number(form.get("monthly_rate")),
      currency: String(form.get("currency")),
      status: "active",
      compliance_agreement: null,
      contract_renewal_date: null,
      contact_email: null,
      notes: null,
    };
    try {
      const response = await fetch(`${API_URL}/suppliers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((issue: { msg?: string }) => issue.msg).join("; ")
          : data.detail;
        throw new Error(detail ?? "No se pudo crear el proveedor.");
      }
      formElement.reset();
      await loadSuppliers();
      window.alert("Proveedor registrado correctamente.");
    } catch (cause) {
      window.alert(cause instanceof Error ? cause.message : "Error de conexión con la API.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f5f7fb] text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-teal-700 text-xl font-bold text-white">H</div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal-700">HealthCore</p>
              <h1 className="text-lg font-bold">Directorio de proveedores</h1>
            </div>
          </div>
          <span className="hidden rounded-full bg-emerald-50 px-3 py-1.5 text-sm font-medium text-emerald-700 sm:inline-flex">Operaciones · Backoffice</span>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-5 py-8 lg:px-8">
        <section className="mb-7 grid gap-4 md:grid-cols-[1fr_auto] md:items-end">
          <div>
            <p className="mb-2 text-sm font-medium text-slate-500">GESTIÓN · PROVEEDORES</p>
            <h2 className="text-3xl font-bold tracking-tight">Controla tus relaciones con proveedores</h2>
            <p className="mt-2 text-slate-600">Consulta, filtra y actualiza la información de tus socios operativos.</p>
          </div>
          <div className="flex gap-3">
            <div className="rounded-2xl border border-slate-200 bg-white px-5 py-3 shadow-sm">
              <p className="text-xs text-slate-500">En este resultado</p><p className="text-xl font-bold">{suppliers.length} <span className="text-sm font-normal text-slate-500">proveedores</span></p>
            </div>
            <div className="rounded-2xl border border-emerald-100 bg-emerald-50 px-5 py-3">
              <p className="text-xs text-emerald-700">Activos</p><p className="text-xl font-bold text-emerald-800">{activeCount}</p>
            </div>
          </div>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="flex flex-col gap-4 border-b border-slate-100 p-5 sm:flex-row sm:items-end sm:justify-between">
            <div><h3 className="font-semibold">Todos los proveedores</h3><p className="mt-1 text-sm text-slate-500">Los filtros se aplican al instante.</p></div>
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="text-xs font-semibold text-slate-600">PAÍS
                <select value={country} onChange={(event) => setCountry(event.target.value)} className="mt-1.5 block w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm font-normal outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100">
                  <option value="">Todos los países</option><option value="USA">Estados Unidos</option><option value="UK">Reino Unido</option>
                </select>
              </label>
              <label className="text-xs font-semibold text-slate-600">CATEGORÍA
                <select value={category} onChange={(event) => setCategory(event.target.value)} className="mt-1.5 block w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm font-normal outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100">
                  <option value="">Todas las categorías</option>{CATEGORIES.map((item) => <option key={item} value={item}>{categoryLabel(item)}</option>)}
                </select>
              </label>
            </div>
          </div>
          {error && <div className="m-5 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">No se pudo cargar la lista: {error}. Comprueba que la API esté activa en {API_URL}.</div>}
          <div className="overflow-x-auto">
            <table className="w-full min-w-[900px] text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500"><tr><th className="px-5 py-3.5">Proveedor</th><th className="px-4 py-3.5">País</th><th className="px-4 py-3.5">Categorías</th><th className="px-4 py-3.5">Tarifa mensual</th><th className="px-4 py-3.5">Cumplimiento</th><th className="px-4 py-3.5">Estado</th><th className="px-5 py-3.5">Acciones</th></tr></thead>
              <tbody className="divide-y divide-slate-100">
                {suppliers.length === 0 ? <tr><td colSpan={7} className="px-5 py-12 text-center text-slate-500">No hay proveedores que coincidan con estos filtros.</td></tr> : suppliers.map((supplier) => (
                  <tr key={supplier.id} className={supplier.status === "suspended" ? "bg-rose-50/80 text-slate-500" : "hover:bg-slate-50/70"}>
                    <td className="px-5 py-4"><span className={`font-semibold ${supplier.status === "suspended" ? "line-through decoration-rose-400" : "text-slate-800"}`}>{supplier.name}</span><span className="mt-1 block text-xs text-slate-400">ID #{supplier.id}</span></td>
                    <td className="px-4 py-4">{supplier.country === "USA" ? "🇺🇸 USA" : "🇬🇧 UK"}</td>
                    <td className="max-w-64 px-4 py-4"><div className="flex flex-wrap gap-1.5">{supplier.categories.map((item) => <span key={item} className="rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-600">{categoryLabel(item)}</span>)}</div></td>
                    <td className="whitespace-nowrap px-4 py-4 font-semibold text-slate-800">{new Intl.NumberFormat("en", { style: "currency", currency: supplier.currency }).format(supplier.monthly_rate)}<span className="ml-1 text-xs font-normal text-slate-400">/ mo</span></td>
                    <td className="px-4 py-4">{supplier.compliance_agreement ? <span className="rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">{supplier.compliance_agreement === "both" ? "BAA + DPA" : supplier.compliance_agreement}</span> : <span className="text-slate-400">No requerido</span>}</td>
                    <td className="px-4 py-4"><span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${supplier.status === "active" ? "bg-emerald-50 text-emerald-700" : "bg-rose-100 text-rose-800"}`}><span className={`h-1.5 w-1.5 rounded-full ${supplier.status === "active" ? "bg-emerald-500" : "bg-rose-600"}`} />{supplier.status === "active" ? "Activo" : "Suspendido"}</span></td>
                    <td className="px-5 py-4"><div className="flex items-center gap-2"><button onClick={() => void editRate(supplier)} className="rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs font-medium text-slate-700 hover:bg-white">Editar tarifa</button><button onClick={() => void toggleStatus(supplier)} className={`rounded-lg px-2.5 py-1.5 text-xs font-medium ${supplier.status === "active" ? "text-rose-700 hover:bg-rose-100" : "text-emerald-700 hover:bg-emerald-100"}`}>{supplier.status === "active" ? "Suspender" : "Activar"}</button></div></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="border-t border-slate-100 px-5 py-3 text-xs text-slate-500">Mostrando {suppliers.length} proveedor{suppliers.length === 1 ? "" : "es"}</div>
        </section>

        <section className="mt-7 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7">
          <div className="mb-5"><p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal-700">Nuevo registro</p><h3 className="mt-1 text-xl font-bold">Añadir proveedor</h3><p className="mt-1 text-sm text-slate-500">La moneda debe coincidir con el país (USA: USD, UK: GBP).</p></div>
          <form onSubmit={createSupplier} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <label className="text-sm font-medium text-slate-700">Nombre<input name="name" required maxLength={120} placeholder="Nombre de la empresa" className="mt-1.5 w-full rounded-lg border border-slate-200 px-3 py-2.5 font-normal outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100" /></label>
            <label className="text-sm font-medium text-slate-700">País<select name="country" required defaultValue="USA" className="mt-1.5 w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 font-normal outline-none focus:border-teal-600"><option value="USA">Estados Unidos</option><option value="UK">Reino Unido</option></select></label>
            <label className="text-sm font-medium text-slate-700">Categoría<select name="categories" required defaultValue="medical_supplies" className="mt-1.5 w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 font-normal outline-none focus:border-teal-600">{CATEGORIES.map((item) => <option key={item} value={item}>{categoryLabel(item)}</option>)}</select></label>
            <label className="text-sm font-medium text-slate-700">Tarifa mensual<input name="monthly_rate" type="number" min="0.01" step="0.01" required placeholder="0.00" className="mt-1.5 w-full rounded-lg border border-slate-200 px-3 py-2.5 font-normal outline-none focus:border-teal-600 focus:ring-2 focus:ring-teal-100" /></label>
            <label className="text-sm font-medium text-slate-700">Moneda<select name="currency" required defaultValue="USD" className="mt-1.5 w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 font-normal outline-none focus:border-teal-600"><option value="USD">USD · Dólar</option><option value="GBP">GBP · Libra</option></select></label>
            <div className="sm:col-span-2 lg:col-span-5"><button type="submit" disabled={saving} className="rounded-lg bg-teal-700 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-teal-800 disabled:cursor-wait disabled:opacity-60">{saving ? "Guardando…" : "+ Registrar proveedor"}</button></div>
          </form>
        </section>
        <p className="py-6 text-center text-xs text-slate-400">HealthCore Supplier Directory · Datos gestionados desde FastAPI</p>
      </div>
    </main>
  );
}
