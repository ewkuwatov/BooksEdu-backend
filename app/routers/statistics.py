from fastapi import APIRouter, Depends
from openpyxl.workbook import Workbook
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.university import University
from app.models.direction import Direction
from app.models.subject import Subject
from app.models.literature import Literature
from app.dependencies import require_owner_or_superadmin
from sqlalchemy.orm import selectinload
from fastapi.responses import StreamingResponse
from io import BytesIO
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side


router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("/export")
async def export_statistics(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_owner_or_superadmin)
):
    # ================================
    # Загрузка данных
    # ================================
    query = (
        select(University)
        .options(
            selectinload(University.directions)
            .selectinload(Direction.subjects)
            .selectinload(Subject.literature)
        )
    )

    if current_user.role == "superadmin":
        query = query.where(University.id == current_user.university_id)

    result = await db.execute(query)
    universities = result.scalars().all()

    wb = Workbook()
    first_sheet = True

    for uni in universities:
        ws = wb.active if first_sheet else wb.create_sheet(title=uni.name)
        ws.title = uni.name
        first_sheet = False

        # ================================
        # Excel настройки
        # ================================
        ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 1
        ws.sheet_view.zoomScale = 75

        # ================================
        # Заголовки
        # ================================
        headers = [
            "Mutaxassislik shifri",
            "Yo'nalish",
            "Talabalar soni",
            "Fan nomi",
            "Adabiyot nomi",
            "Turi",
            "Muallif",
            "Nashriyot",
            "Til",
            "Yozuvi",
            "Yili",
            "Bosma",
            "Elektron",
            "Ta’minlanganlik %"
        ]

        headers = ["\n".join(h.split()) for h in headers]
        ws.append(headers)

        # ================================
        # Стили
        # ================================
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill("solid", fgColor="4F81BD")
        align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin")
        )

        # ================================
        # Сбор данных
        # ================================
        direction_students = {
            d.number: d.student_count or 0 for d in uni.directions
        }

        rows = []
        unique = set()

        for direction in uni.directions:
            total = direction_students[direction.number]

            for subject in direction.subjects:
                for lit in subject.literature:
                    percent = 100 if lit.file_path else min(
                        int((lit.printed_count or 0) * 6 / max(total, 1) * 100),
                        100
                    )

                    key = (lit.title, lit.author, lit.publisher, lit.year, percent)
                    if key in unique:
                        continue
                    unique.add(key)

                    rows.append([
                        direction.number,
                        direction.name,
                        total,
                        subject.name,
                        lit.title,
                        lit.kind,
                        lit.author or "",
                        lit.publisher or "",
                        getattr(lit.language, "value", lit.language),
                        getattr(lit.font_type, "value", lit.font_type),
                        lit.year,
                        lit.printed_count or 0,
                        "✓" if lit.file_path else "",
                        f"{percent}%"
                    ])

        rows.sort(key=lambda x: (x[1], x[3]))

        for row in rows:
            ws.append(row)

        # ================================
        # MERGE (исправленный)
        # ================================
        merge_cols = [1, 2, 3, 4]
        last_vals = [None] * len(merge_cols)
        start_rows = [2] * len(merge_cols)

        for i, row in enumerate(rows, start=2):
            for idx, col in enumerate(merge_cols):
                if last_vals[idx] != row[col - 1]:
                    if i - 1 > start_rows[idx]:
                        ws.merge_cells(
                            start_row=start_rows[idx],
                            end_row=i - 1,
                            start_column=col,
                            end_column=col
                        )
                    last_vals[idx] = row[col - 1]
                    start_rows[idx] = i

        last_row = len(rows) + 1
        for idx, col in enumerate(merge_cols):
            if last_row > start_rows[idx]:
                ws.merge_cells(
                    start_row=start_rows[idx],
                    end_row=last_row,
                    start_column=col,
                    end_column=col
                )

        # ================================
        # Размеры и стили
        # ================================
        for col in ws.columns:
            length = max(len(str(c.value)) if c.value else 0 for c in col)
            ws.column_dimensions[col[0].column_letter].width = min(length + 2, 30)

        for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
            ws.row_dimensions[row[0].row].height = 35
            for cell in row:
                cell.alignment = align
                cell.border = border

        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col)
            cell.font = header_font
            cell.fill = header_fill

    # ================================
    # Ответ
    # ================================
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=statistics.xlsx",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )
