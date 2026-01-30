from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
from openpyxl import Workbook

from app.db.session import get_db
from app.models.analysis.library_fund import LibraryFund
from app.models.analysis.literature_reports import LiteratureReport

router = APIRouter()


@router.get("/export/library-excel")
def export_library_excel(db: Session = Depends(get_db)):

    wb = Workbook()

    # =========================
    # 1️⃣ Лист: Library Fund
    # =========================
    ws1 = wb.active
    ws1.title = "ARM_FUND"

    ws1.append([
        "OTM ID",
        "ARM nomda", "ARM nusxada",
        "Uzbek (kiril)", "Uzbek (lotin)", "Rus", "Ingliz", "Boshqa",
        "Bosma", "Elektron", "Brayl", "Audio",
        "O‘quv", "Ilmiy", "Badiiy", "Xorijiy", "Boshqa"
    ])

    funds = db.query(LibraryFund).all()

    for f in funds:
        ws1.append([
            f.university_id,
            f.arm_fond_nomi,
            f.arm_fond_nusxada,
            f.uz_kiril,
            f.uz_lotin,
            f.rus,
            f.ingliz,
            f.boshqa_tillar,
            f.bosma,
            f.elektron,
            f.brayl,
            f.audio,
            f.oquv_adabiyot,
            f.ilmiy_adabiyot,
            f.badiiy_adabiyot,
            f.xorijiy_adabiyot,
            f.boshqa_adabiyot,
        ])

    # =========================
    # 2️⃣ Лист: Literature Report
    # =========================
    ws2 = wb.create_sheet(title="LITERATURE_REPORT")

    ws2.append([
        "OTM ID",
        "Darslik (nomda)", "Darslik (nusxada)",
        "O‘quv qo‘llanma (nomda)", "O‘quv qo‘llanma (nusxada)",
        "Uslubiy (nomda)", "Uslubiy (nusxada)",
        "Lug‘at (nomda)", "Lug‘at (nusxada)",
        "Uslubiy ko‘rsatma (nomda)", "Uslubiy ko‘rsatma (nusxada)",
        "Tavsiyanoma (nomda)", "Tavsiyanoma (nusxada)",
        "Ma’lumotnoma (nomda)", "Ma’lumotnoma (nusxada)",
        "Ma’ruza (nomda)", "Ma’ruza (nusxada)",
        "Mashq (nomda)", "Mashq (nusxada)",
        "Daydjest (nomda)", "Daydjest (nusxada)",
    ])

    reports = db.query(LiteratureReport).all()

    for r in reports:
        ws2.append([
            r.university_id,
            r.darslik_nomda, r.darslik_nusxada,
            r.oq_qollanma_nomda, r.oq_qollanma_nusxada,
            r.uslubiy_nomda, r.uslubiy_nusxada,
            r.lugat_nomda, r.lugat_nusxada,
            r.uslubiy_korsatma_nomda, r.uslubiy_korsatma_nusxada,
            r.uslubiy_tavsiyanoma_nomda, r.uslubiy_tavsiyanoma_nusxada,
            r.malumotlar_nomda, r.malumotlar_nusxada,
            r.maruzalar_nomda, r.maruzalar_nusxada,
            r.mashqlar_nomda, r.mashqlar_nusxada,
            r.daydjest_nomda, r.daydjest_nusxada,
        ])

    # =========================
    # File response
    # =========================
    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=library_report.xlsx"
        }
    )
