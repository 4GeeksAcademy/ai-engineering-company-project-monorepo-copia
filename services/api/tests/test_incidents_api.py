import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import api.incidents.router as incidents_router
from api.main import app

OFFICIAL_CSV = Path(__file__).resolve().parents[3] / "scripts" / "incidents-healthcore.csv"
HEADER = (
    "incident_id,date,clinic_id,country,category,description,status,"
    "patient_id,satisfaction_score\n"
)


class IncidentsApiTests(unittest.TestCase):
    def setUp(self):
        incidents_router.latest_result = None
        self.client = TestClient(app)

    def post_file(self, name, content, content_type="text/csv"):
        return self.client.post(
            "/api/incidents/analyze", files={"file": (name, content, content_type)}
        )

    def test_analyze_official_csv(self):
        response = self.post_file("incidents.csv", OFFICIAL_CSV.read_bytes())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_records"], 100)
        self.assertEqual(data["valid_records"], 94)
        self.assertEqual(data["invalid_records"], 6)
        self.assertEqual(data["satisfaction"]["average_score"], 3.58)
        self.assertEqual(data["categories"]["APPOINTMENT"]["count"], 30)
        self.assertEqual(data["statuses"]["CLOSED"]["count"], 52)
        self.assertEqual(data["countries"]["US"]["count"], 61)
        self.assertNotIn("PAT-", response.text)

    def test_export_after_analysis(self):
        self.post_file("incidents.csv", OFFICIAL_CSV.read_bytes())
        response = self.client.get("/api/incidents/results/export")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.text.startswith("metric,value,percentage"))
        self.assertNotIn("PAT-", response.text)

    def test_export_before_analysis_returns_404(self):
        response = self.client.get("/api/incidents/results/export")
        self.assertEqual(response.status_code, 404)

    def test_request_without_file(self):
        response = self.client.post("/api/incidents/analyze")
        self.assertIn(response.status_code, (400, 422))

    def test_empty_csv(self):
        self.assertEqual(self.post_file("vacio.csv", b"").status_code, 400)

    def test_not_a_csv_extension(self):
        response = self.post_file("datos.txt", b"hola", "text/plain")
        self.assertEqual(response.status_code, 400)

    def test_binary_file_with_csv_extension(self):
        self.assertEqual(self.post_file("raro.csv", b"\xff\xfe\x00\x80\x81").status_code, 400)

    def test_missing_columns(self):
        self.assertEqual(self.post_file("x.csv", b"a,b,c\n1,2,3\n").status_code, 400)

    def test_header_only(self):
        self.assertEqual(self.post_file("x.csv", HEADER.encode()).status_code, 400)


if __name__ == "__main__":
    unittest.main()