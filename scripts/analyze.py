import argparse
import sys
from pathlib import Path


API_SOURCE = Path(__file__).resolve().parents[1] / "services" / "api" / "src"
sys.path.insert(0, str(API_SOURCE))

from api.incidents.analysis import CSVAnalysisError, AnalysisResult, analyze_csv


def print_breakdown(title: str, values: dict[str, int]) -> None:
    print(f"\n{title}")
    if not values:
        print("  Sin registros")
        return
    label_width = max(len(label) for label in values)
    for label, count in values.items():
        print(f"  {label:<{label_width}}  {count:>5}")


def print_summary(result: AnalysisResult) -> None:
    print("=" * 64)
    print("ANÁLISIS DE INCIDENCIAS · HEALTHCORE")
    print("=" * 64)
    print(f"Registros procesados : {result.total_processed}")
    print(f"Registros válidos    : {result.valid_records}")
    print(f"Registros inválidos  : {result.invalid_records}")

    if result.invalid_by_reason:
        print_breakdown("Incidencias por tipo de problema:", result.invalid_by_reason)
        print("\nFilas con problemas (sin mostrar datos personales):")
        for invalid in result.invalid_record_details:
            print(f"  Fila {invalid['row_number']}: {', '.join(invalid['reasons'])}")

    print_breakdown("Incidencias por categoría:", result.categories)
    print_breakdown("Incidencias por estado:", result.states)
    average = result.closed_case_satisfaction_avg
    average_text = "Sin puntuaciones registradas" if average is None else f"{average:.2f} / 5"
    print(f"\nSatisfacción media en casos cerrados: {average_text}")
    print("=" * 64)


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida y resume un CSV de incidencias HealthCore.")
    parser.add_argument("csv_path", type=Path, help="Ruta al fichero CSV de incidencias")
    args = parser.parse_args()

    try:
        result = analyze_csv(args.csv_path.read_bytes())
    except OSError as error:
        print(f"No se pudo leer el fichero: {error}", file=sys.stderr)
        return 1
    except CSVAnalysisError as error:
        print(f"CSV no válido: {error}", file=sys.stderr)
        return 1

    print_summary(result)
    try:
        answer = input("\n¿Deseas exportar los resultados a CSV? [s / n]: ").strip().lower()
    except EOFError:
        answer = "n"
    if answer == "s":
        Path("results.csv").write_text(result.to_csv(), encoding="utf-8", newline="")
        print("Resultados agregados guardados en results.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())