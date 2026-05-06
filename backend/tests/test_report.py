"""Report export API tests."""
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.config import settings


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_export_docx_creates_file(client: TestClient, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "files_dir", tmp_path)
    monkeypatch.setattr(settings, "report_template_docx", _repo_root() / "templates/report/jinja_minimal.docx")
    r = client.post("/api/projects", json={"name": "rpt"})
    pid = r.json()["id"]
    r2 = client.post(f"/api/projects/{pid}/reports/docx")
    assert r2.status_code == 200
    rel = r2.json()["docx_relpath"]
    assert rel.endswith(".docx")
    f = tmp_path / rel
    assert f.is_file() and f.stat().st_size > 500


def test_export_pdf_uses_libreoffice_or_mock(client: TestClient, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "files_dir", tmp_path)
    monkeypatch.setattr(settings, "report_template_docx", _repo_root() / "templates/report/jinja_minimal.docx")
    r = client.post("/api/projects", json={"name": "pdf-proj"})
    pid = r.json()["id"]

    def _fake_pdf(docx: Path, pdf: Path) -> None:
        pdf.write_bytes(b"%PDF-1.4 fake")

    with patch("app.routers.reports.docx_to_pdf", side_effect=_fake_pdf):
        r2 = client.post(f"/api/projects/{pid}/reports/pdf")
    assert r2.status_code == 200
    prel = r2.json()["pdf_relpath"]
    assert (tmp_path / prel).is_file()


def test_export_pdf_503_when_converter_missing(client: TestClient, tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "files_dir", tmp_path)
    monkeypatch.setattr(settings, "report_template_docx", _repo_root() / "templates/report/jinja_minimal.docx")
    r = client.post("/api/projects", json={"name": "noffice"})
    pid = r.json()["id"]
    from app.services.pdf_export import PdfExportError

    with patch(
        "app.routers.reports.docx_to_pdf",
        side_effect=PdfExportError("LibreOffice (soffice) not found on PATH"),
    ):
        r2 = client.post(f"/api/projects/{pid}/reports/pdf")
    assert r2.status_code == 503
