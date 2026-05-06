"""Convert DOCX to PDF using LibreOffice/soffice when installed."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class PdfExportError(RuntimeError):
    pass


def _soffice_candidates() -> list[str]:
    out: list[str] = []
    for name in ("soffice", "soffice.exe"):
        p = shutil.which(name)
        if p:
            out.append(p)
    win = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
    if win.is_file() and str(win) not in out:
        out.append(str(win))
    win32 = Path(r"C:\Program Files (x86)\LibreOffice\program\soffice.exe")
    if win32.is_file() and str(win32) not in out:
        out.append(str(win32))
    return out


def docx_to_pdf(docx: Path, pdf_out: Path) -> None:
    if not docx.is_file():
        raise PdfExportError(f"docx not found: {docx}")
    pdf_out.parent.mkdir(parents=True, exist_ok=True)
    outdir = docx.parent
    cands = _soffice_candidates()
    if not cands:
        raise PdfExportError("LibreOffice (soffice) not found on PATH")
    last_err: str | None = None
    for exe in cands:
        try:
            subprocess.run(
                [exe, "--headless", "--convert-to", "pdf", "--outdir", str(outdir), str(docx)],
                check=True,
                capture_output=True,
                text=True,
                timeout=180,
            )
        except (subprocess.CalledProcessError, OSError, subprocess.TimeoutExpired) as e:
            last_err = str(e)
            continue
        expect = outdir / f"{docx.stem}.pdf"
        if not expect.is_file():
            last_err = "converter finished but pdf missing"
            continue
        if expect.resolve() != pdf_out.resolve():
            if pdf_out.exists():
                pdf_out.unlink()
            shutil.move(str(expect), str(pdf_out))
        return
    raise PdfExportError(last_err or "conversion failed")
