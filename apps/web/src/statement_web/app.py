"""FastAPI app wrapping the pdf_statement_converter tool."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from accounting_core import Money
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from pdf_statement_converter import convert

app = FastAPI(title="Statement Converter", version="0.1.0")

_STATIC = Path(__file__).parent / "static"


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (_STATIC / "index.html").read_text(encoding="utf-8")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _serialize(result: Any, filename: str) -> dict[str, Any]:
    rows = [
        {
            "date": r.date.isoformat(),
            "description": r.description,
            "amount": str(r.amount.amount),
            "balance": None if r.balance is None else str(r.balance.amount),
            "currency": r.amount.currency,
        }
        for r in result.rows
    ]

    balance_check = None
    bc = result.balance_check
    if bc is not None:
        balance_check = {
            "ok": bc.ok,
            "checked": bc.checked,
            "discrepancies": [
                {
                    "index": d.index,
                    "date": d.date.isoformat(),
                    "description": d.description,
                    "expected": str(d.expected_balance.amount),
                    "actual": str(d.actual_balance.amount),
                    "difference": str(d.difference.amount),
                }
                for d in bc.discrepancies
            ],
        }

    return {
        "filename": filename,
        "count": len(rows),
        "rows": rows,
        "csv": result.csv_text,
        "balance_check": balance_check,
    }


@app.post("/api/convert")
async def api_convert(
    file: UploadFile = File(...),
    strategy: str = Form("auto"),
    currency: str = Form("USD"),
    dayfirst: bool = Form(False),
    opening_balance: str = Form(""),
) -> JSONResponse:
    filename = file.filename or "statement.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a .pdf file.")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    currency = (currency or "USD").strip().upper() or "USD"
    opening = None
    if opening_balance.strip():
        try:
            opening = Money.of(opening_balance.strip(), currency)
        except Exception as exc:  # noqa: BLE001 - surface a clean 400 to the client
            raise HTTPException(
                status_code=400, detail=f"Invalid opening balance: {exc}"
            ) from exc

    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
        tmp.write(data)
        tmp.flush()
        try:
            result = convert(
                tmp.name,
                strategy=strategy,
                currency=currency,
                dayfirst=dayfirst,
                opening_balance=opening,
            )
        except (ValueError, IndexError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return JSONResponse(_serialize(result, filename))


def main() -> None:
    """Console entry point: run the development server."""
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
