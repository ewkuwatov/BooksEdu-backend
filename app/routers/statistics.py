from fastapi import APIRouter, Depends, HTTPException
from openpyxl.workbook import Workbook
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.models.university import University
from app.models.direction import Direction
from app.models.subject import Subject
from app.models.literature import Literature
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.dependencies import require_owner_or_superadmin
from sqlalchemy.orm import selectinload
from collections import defaultdict
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

router = APIRouter(prefix="/statistics", tags=["statistics"])

@router.get("/export")
async def export_statistics(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_owner_or_superadmin)
):
    # Загружаем университеты с selectinload связей
    if current_user.role == "superadmin":
        query = (
            select(University)
            .options(
                selectinload(University.directions)
                .selectinload(Direction.subjects)
                .selectinload(Subject.literature)
            )
            .where(University.id == current_user.university_id)
        )
    else:  # owner
        query = (
            select(University)
            .options(
                selectinload(University.directions)
                .selectinload(Direction.subjects)
                .selectinload(Subject.literature)
            )
        )

    result = await db.execute(query)
    universities = result.scalars().all()

    wb = Workbook()
    first_sheet = True

    for uni in universities:
        if first_sheet:
            ws = wb.active
            ws.title = uni.name
            first_sheet = False
        else:
            ws = wb.create_sheet(title=uni.name)

        headers = [
            "Direction.number", "Direction.name", "Direction.course", "Direction.student_count",
            "Subject.name", "Literature.title", "Literature.kind", "Author", "Publisher",
            "Language", "Font_type", "Year", "Printed_count", "Electron", "Available_percent"
        ]

        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
        center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        thin_border = Border(left=Side(style="thin"), right=Side(style="thin"),
                             top=Side(style="thin"), bottom=Side(style="thin"))
        ws.append(headers)

        # Собираем все строки сначала
        rows = []
        for direction in uni.directions:
            for subject in direction.subjects:
                for lit in subject.literature:
                    electron_status = "available" if lit.file_path else ""
                    if lit.file_path:
                        percent_available = 100
                    else:
                        K = lit.printed_count or 0
                        T = direction.student_count or 1
                        percent_available = min(int((K * 6 / T) * 100), 100)

                    row = [
                        direction.number,
                        direction.name,
                        direction.course,
                        direction.student_count,
                        subject.name,
                        lit.title,
                        lit.kind,
                        lit.author or "",
                        lit.publisher or "",
                        lit.language.value,
                        lit.font_type.value,
                        lit.year,
                        lit.printed_count or 0,
                        electron_status,
                        f"{percent_available}%",
                    ]
                    rows.append(row)

        # Добавляем строки в Excel
        start_row = 2
        for r in rows:
            ws.append(r)

        # Объединяем повторяющиеся Direction + Subject колонки
        merge_cols = [1, 2, 3, 4, 5]
        current_vals = [None] * len(merge_cols)
        start_merge = [2] * len(merge_cols)

        for i, row in enumerate(rows, start=2):
            for idx, col in enumerate(merge_cols):
                if current_vals[idx] != row[col - 1]:
                    if i - 1 > start_merge[idx]:
                        ws.merge_cells(
                            start_row=start_merge[idx],
                            end_row=i - 1,
                            start_column=col,
                            end_column=col
                        )
                    current_vals[idx] = row[col - 1]
                    start_merge[idx] = i

        # Финальный merge для оставшихся
        for idx, col in enumerate(merge_cols):
            if start_merge[idx] < len(rows) + 1:
                ws.merge_cells(
                    start_row=start_merge[idx],
                    end_row=len(rows) + 1,
                    start_column=col,
                    end_column=col
                )

        # Автоширина колонок
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            ws.column_dimensions[column].width = max_length + 2

        # Выровнять все данные по центру
        for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
            for cell in row:
                cell.alignment = Alignment(horizontal="center", vertical="center")

        # Применяем стили к заголовку
        for col_num, column_title in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=column_title)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = thin_border

        # Применяем стили ко всем данным
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
            for cell in row:
                cell.alignment = center_align
                cell.border = thin_border

        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column].width = max_length + 2  # сейчас +2

        for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
            ws.row_dimensions[row[0].row].height = 30

    # Сохраняем Excel в поток
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=statistics.xlsx"}
    )
