from __future__ import annotations

import io
from pathlib import Path

import pytest
from docx import Document

from esg_commitment_audit.ingest import (
    _layout_text_regions,
    _table_role_map,
    ingest_bytes,
    ingest_path,
)


def _minimal_pdf(text: str) -> bytes:
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET".encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
        ),
        b"<< /Length "
        + str(len(stream)).encode()
        + b" >>\nstream\n"
        + stream
        + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode())
        output.extend(body)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode()
    )
    return bytes(output)


def test_ingest_plain_text() -> None:
    document = ingest_bytes(
        "第一段\n\n环境\n\n公司承诺到2030年减少碳排放。".encode(),
        "report.txt",
    )
    assert document.extension == ".txt"
    assert len(document.blocks) == 3
    assert document.blocks[-2].section == "环境"
    assert document.character_count > 10


def test_ingest_docx() -> None:
    buffer = io.BytesIO()
    word = Document()
    word.add_heading("环境", level=1)
    word.add_paragraph("公司承诺到2030年减少碳排放。")
    table = word.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "范围"
    table.cell(0, 1).text = "Scope 1"
    word.save(buffer)

    document = ingest_bytes(buffer.getvalue(), "report.docx")
    assert len(document.blocks) == 3
    assert any("Scope 1" in block.text for block in document.blocks)


def test_ingest_pdf_text_layer() -> None:
    pdf = _minimal_pdf("We commit to net zero by 2040.")
    document = ingest_bytes(pdf, "report.pdf")
    assert document.extension == ".pdf"
    assert "net zero" in document.blocks[0].text.lower()
    assert document.blocks[0].page_number == 1


def test_unsupported_and_empty_input() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        ingest_bytes(b"data", "report.csv")
    with pytest.raises(ValueError, match="empty"):
        ingest_bytes(b"", "report.txt")


@pytest.mark.parametrize(
    ("filename", "content"),
    [
        ("broken.pdf", b"not a pdf"),
        ("broken.docx", b"not a docx"),
    ],
)
def test_malformed_document_raises_clean_value_error(
    filename: str,
    content: bytes,
) -> None:
    with pytest.raises(ValueError, match="could not be parsed"):
        ingest_bytes(content, filename)


def test_ingest_path() -> None:
    path = Path("examples/strong_commitment.txt")
    document = ingest_path(path)
    assert document.filename == path.name
    assert document.blocks


class _Box:
    def __init__(self, left: float, top: float, right: float, bottom: float) -> None:
        self.bbox = (left, top, right, bottom)


class _TablePage:
    def __init__(self, cells: dict[tuple[int, int], str]) -> None:
        self._cells = cells

    def crop(self, bbox: tuple[float, float, float, float]) -> _TableCell:
        return _TableCell(self._cells[bbox])


class _TableCell:
    def __init__(self, text: str) -> None:
        self._text = text

    def extract_text(self) -> str:
        return self._text


def _table_with_cells(
    cells: list[list[str]],
) -> tuple[_TablePage, object]:
    rows = [_Box(0, index * 10, 30, (index + 1) * 10) for index in range(len(cells))]
    width = max(len(row) for row in cells)
    columns = [_Box(index * 20, 0, (index + 1) * 20, 30) for index in range(width)]
    cell_texts: dict[tuple[float, float, float, float], str] = {}
    for row_index, row in enumerate(cells):
        for column_index, text in enumerate(row):
            bbox = (
                columns[column_index].bbox[0],
                rows[row_index].bbox[1],
                columns[column_index].bbox[2],
                rows[row_index].bbox[3],
            )
            cell_texts[bbox] = text
    return _TablePage(cell_texts), type(
        "Table", (), {"rows": rows, "columns": columns}
    )()


def test_table_role_map_marks_target_and_progress_columns() -> None:
    page, table = _table_with_cells(
        [
            ["指标", "管理目标", "管理进展"],
            ["能源", "到2030年清洁能源比例达到80%", "2024年已达到52%"],
        ]
    )

    roles = _table_role_map(page, table)

    assert roles[(0, 1)] == "target"
    assert roles[(0, 2)] == "progress"
    assert roles[(1, 1)] == "target"
    assert roles[(1, 2)] == "progress"


def test_table_role_map_marks_alternating_target_and_progress_rows() -> None:
    page, table = _table_with_cells(
        [
            ["目标", "到2030年将范围1和范围2碳排放减少50%"],
            ["进展", "2024年已减少18%"],
            ["目标", "到2035年实现100%可再生电力"],
            ["进展", "2024年达到71%"],
        ]
    )

    roles = _table_role_map(page, table)

    assert roles[(0, 1)] == "target"
    assert roles[(1, 1)] == "progress"
    assert roles[(2, 1)] == "target"
    assert roles[(3, 1)] == "progress"


def test_layout_text_regions_keep_columns_separate() -> None:
    layout = (
        "        Emissions                    Materials\n"
        "        Reduce emissions by 2030.            Use recycled materials by 2030.\n"
    )

    regions = _layout_text_regions(layout)
    texts = [region.text for region in regions]

    assert any("Reduce emissions" in text for text in texts)
    assert any("recycled materials" in text for text in texts)
    assert not any(
        "Reduce emissions" in text and "recycled materials" in text for text in texts
    )


def test_layout_text_regions_propagate_target_and_progress_roles() -> None:
    layout = (
        "              目标及承诺\n"
        "      能源        到2030年清洁能源比例达到80%\n"
        "      进展        2024年已达到52%\n"
    )

    regions = _layout_text_regions(layout)

    assert any(
        "清洁能源比例" in region.text and region.table_role == "target"
        for region in regions
    )
    assert any(
        "2024年已达到52%" in region.text and region.table_role == "progress"
        for region in regions
    )
