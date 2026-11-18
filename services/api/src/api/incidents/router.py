from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from api.incidents.analysis import AnalysisResult, CSVAnalysisError, analyze_csv


router = APIRouter(prefix="/api/incidents", tags=["incidents"])
latest_result: AnalysisResult | None = None


@router.post("/analyze")
async def analyze_incidents(file: UploadFile = File(...)) -> dict:
    global latest_result

    if not file.filename:
        raise HTTPException(status_code=400, detail="Debes seleccionar un fichero CSV.")
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="El fichero debe tener extensión .csv.")

    content = await file.read()
    try:
        result = analyze_csv(content)
    except CSVAnalysisError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    finally:
        await file.close()

    latest_result = result
    return result.to_dict()


@router.get("/results/export")
def export_results() -> Response:
    if latest_result is None:
        raise HTTPException(
            status_code=404,
            detail="Todavía no hay resultados. Analiza un CSV primero.",
        )

    return Response(
        content=latest_result.to_csv(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="resultados_healthcore.csv"'},
    )
