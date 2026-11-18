import csv
import io
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any


REQUIRED_FIELDS = ("id_incidencia", "departamento", "categoria", "estado")
VALID_CATEGORIES = (
    "Documentacion",
    "Citas",
    "Rechazo de reclamos",
    "Fallo de sistema",
    "Onboarding",
)
VALID_STATES = ("abierto", "cerrado", "descartado")


class CSVAnalysisError(ValueError):
    """Raised when the uploaded CSV cannot be analyzed."""


@dataclass(frozen=True)
class AnalysisResult:
    total_processed: int
    valid_records: int
    invalid_records: int
    invalid_by_reason: dict[str, int]
    invalid_record_details: list[dict[str, Any]]
    categories: dict[str, int]
    states: dict[str, int]
    closed_case_satisfaction_avg: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_processed": self.total_processed,
            "valid_records": self.valid_records,
            "invalid_records": self.invalid_records,
            "invalid_by_reason": self.invalid_by_reason,
            "invalid_record_details": self.invalid_record_details,
            "categories": self.categories,
            "states": self.states,
            "closed_case_satisfaction_avg": self.closed_case_satisfaction_avg,
        }

    def to_csv(self) -> str:
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(("metric", "dimension", "value"))
        writer.writerow(("total_processed", "", self.total_processed))
        writer.writerow(("valid_records", "", self.valid_records))
        writer.writerow(("invalid_records", "", self.invalid_records))
        for reason, count in sorted(self.invalid_by_reason.items()):
            writer.writerow(("invalid_by_reason", reason, count))
        for category, count in sorted(self.categories.items()):
            writer.writerow(("incidents_by_category", category, count))
        for state, count in sorted(self.states.items()):
            writer.writerow(("incidents_by_state", state, count))
        writer.writerow((
            "closed_case_satisfaction_avg",
            "",
            "" if self.closed_case_satisfaction_avg is None else self.closed_case_satisfaction_avg,
        ))
        return output.getvalue()


def _iter_numbered_rows(reader: csv.DictReader) -> Iterator[tuple[int, dict[Any, Any]]]:
    try:
        yield from enumerate(reader, start=2)
    except csv.Error as error:
        raise CSVAnalysisError(f"El CSV tiene una estructura incorrecta: {error}") from error


def analyze_csv(content: bytes | str) -> AnalysisResult:
    if isinstance(content, bytes):
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise CSVAnalysisError("El fichero debe estar codificado en UTF-8.") from error
    else:
        text = content.lstrip("\ufeff")

    if not text.strip():
        raise CSVAnalysisError("El fichero CSV está vacío.")

    try:
        reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
        headers = reader.fieldnames
    except csv.Error as error:
        raise CSVAnalysisError(f"No se pudo leer el CSV: {error}") from error

    if not headers:
        raise CSVAnalysisError("El CSV debe incluir una fila de encabezados.")
    if len(headers) != len(set(headers)):
        raise CSVAnalysisError("El CSV contiene nombres de columna duplicados.")

    missing_headers = [field for field in REQUIRED_FIELDS if field not in headers]
    if missing_headers:
        raise CSVAnalysisError(
            "Faltan columnas obligatorias: " + ", ".join(missing_headers)
        )

    valid_rows: list[dict[str, str | None]] = []
    invalid_details: list[dict[str, Any]] = []
    invalid_reasons: Counter[str] = Counter()

    for row_number, row in _iter_numbered_rows(reader):
        if row is None or all(value is None or not value.strip() for value in row.values()):
            continue

        reasons: list[str] = []
        if None in row:
            reasons.append("malformed_row")

        for field in REQUIRED_FIELDS:
            value = row.get(field)
            if value is None or not value.strip():
                reasons.append(f"missing_field:{field}")

        category = (row.get("categoria") or "").strip()
        if category and category not in VALID_CATEGORIES:
            reasons.append("invalid_category")

        state = (row.get("estado") or "").strip()
        if state and state not in VALID_STATES:
            reasons.append("invalid_state")

        if reasons:
            invalid_reasons.update(reasons)
            invalid_details.append({"row_number": row_number, "reasons": reasons})
        else:
            valid_rows.append({
                key: value.strip() if value is not None else None
                for key, value in row.items()
                if key is not None
            })

    total_processed = len(valid_rows) + len(invalid_details)
    if total_processed == 0:
        raise CSVAnalysisError("El CSV no contiene registros para analizar.")

    categories = Counter(row["categoria"] for row in valid_rows)
    states = Counter(row["estado"] for row in valid_rows)
    satisfaction_scores: list[float] = []
    for row in valid_rows:
        if row["estado"] != "cerrado":
            continue
        score = (row.get("satisfaccion") or "").strip()
        if not score:
            continue
        try:
            satisfaction_scores.append(float(score))
        except ValueError:
            continue

    satisfaction_avg = (
        round(sum(satisfaction_scores) / len(satisfaction_scores), 2)
        if satisfaction_scores
        else None
    )

    return AnalysisResult(
        total_processed=total_processed,
        valid_records=len(valid_rows),
        invalid_records=len(invalid_details),
        invalid_by_reason=dict(sorted(invalid_reasons.items())),
        invalid_record_details=invalid_details,
        categories=dict(sorted(categories.items())),
        states=dict(sorted(states.items())),
        closed_case_satisfaction_avg=satisfaction_avg,
    )
