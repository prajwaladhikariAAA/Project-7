from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from statement_web import app

reportlab_canvas = pytest.importorskip("reportlab.pdfgen.canvas")

client = TestClient(app)


def _statement_pdf_bytes() -> bytes:
    import io

    buffer = io.BytesIO()
    c = reportlab_canvas.Canvas(buffer)
    text = c.beginText(50, 800)
    text.setFont("Courier", 11)
    for line in [
        "Date        Description        Amount     Balance",
        "01/05/2026  ACME deposit       1,200.00   6,200.00",
        "01/07/2026  Coffee shop          (4.50)   6,195.50",
    ]:
        text.textLine(line)
    c.drawText(text)
    c.save()
    return buffer.getvalue()


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_index_served():
    res = client.get("/")
    assert res.status_code == 200
    assert "Statement Converter" in res.text


def test_convert_returns_rows_csv_and_balance_check():
    files = {"file": ("statement.pdf", _statement_pdf_bytes(), "application/pdf")}
    res = client.post(
        "/api/convert",
        files=files,
        data={"strategy": "text", "opening_balance": "5000.00"},
    )
    assert res.status_code == 200
    body = res.json()

    assert body["count"] == 2
    assert body["rows"][0]["amount"] == "1200.00"
    assert body["rows"][1]["amount"] == "-4.50"
    assert body["csv"].startswith("date,description,amount,balance,currency")
    assert body["balance_check"]["ok"] is True
    assert body["balance_check"]["checked"] == 2


def test_non_pdf_upload_is_rejected():
    files = {"file": ("notes.txt", b"hello", "text/plain")}
    res = client.post("/api/convert", files=files)
    assert res.status_code == 400
    assert "pdf" in res.json()["detail"].lower()


def test_corrupt_pdf_returns_400():
    files = {"file": ("bad.pdf", b"not a real pdf", "application/pdf")}
    res = client.post("/api/convert", files=files, data={"strategy": "text"})
    assert res.status_code == 400
    assert "could not read" in res.json()["detail"].lower()
