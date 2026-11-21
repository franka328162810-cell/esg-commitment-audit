from __future__ import annotations

import hashlib
import io
import re
from dataclasses import dataclass
from pathlib import Path
from zipfile import BadZipFile

import pdfplumber
from docx import Document
from docx.opc.exceptions import PackageNotFoundError
from lxml.etree import XMLSyntaxError
from pdfminer.pdfparser import PDFSyntaxError
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from .models import DocumentBlock, IngestedDocument

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".markdown"}
BULLET_RE = re.compile(r"^\s*(?:[■•▪◦●◆◇\uf0a7\uf0b7]|[0-9]+[.)])\s*")


@dataclass
class _TextRegion:
    x0: float
    top: float
    x1: float
    bottom: float
    text: str
    table_role: str = "neutral"

    @property
    def center_y(self) -> float:
        return (self.top + self.bottom) / 2


def _heading_like(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if stripped.startswith("#"):
        return True
    if "goals and progress" in stripped.casefold() or "目标及承诺" in stripped:
        return True
    if stripped.casefold() in {
        "环境",
        "社会",
        "治理",
        "environment",
        "social",
        "governance",
        "environmental",
        "climate",
    }:
        return True
    if (
        len(stripped) <= 120
        and not re.search(r"[。！？!?\.]", stripped)
        and re.search(
            r"(?:报告|声明|披露|政策|白皮书|report|statement|disclosure|policy|whitepaper)",
            stripped,
            re.IGNORECASE,
        )
    ):
        return True
    if len(stripped) > 90:
        return False
    return bool(
        re.match(
            r"^(?:第[一二三四五六七八九十百\d]+[章节部分]|[一二三四五六七八九十]+、|\d+(?:\.\d+)*[、.)：])",
            stripped,
        )
    )


def _split_plain_text(text: str) -> list[str]:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    result: list[str] = []
    buffer: list[str] = []

    def flush() -> None:
        if buffer:
            result.append(" ".join(buffer).strip())
            buffer.clear()

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            flush()
            continue
        if BULLET_RE.match(line):
            flush()
            buffer.append(line)
            continue
        if _heading_like(line):
            flush()
            result.append(line)
            continue
        buffer.append(line)
    flush()
    return [unit for unit in result if unit]


def _ingest_pdf(data: bytes) -> tuple[list[DocumentBlock], list[str]]:
    reader = PdfReader(io.BytesIO(data))
    blocks: list[DocumentBlock] = []
    warnings: list[str] = []
    paragraph_index = 0
    current_section: str | None = None
    used_layout_blocks = False

    with pdfplumber.open(io.BytesIO(data)) as plumber_pdf:
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception as exc:  # noqa: BLE001 - isolate a malformed page.
                warnings.append(f"Page {page_number} could not be parsed: {exc}")
                continue
            pdf_page = None
            if _page_needs_layout(text):
                used_layout_blocks = True
                pdf_page = plumber_pdf.pages[page_number - 1]
                try:
                    layout_text = page.extract_text(extraction_mode="layout") or text
                except Exception:  # noqa: BLE001 - fall back to geometric layout.
                    layout_text = ""
                cjk_count = len(re.findall(r"[\u3400-\u9fff]", text))
                visible_count = len(re.sub(r"\s+", "", text))
                if visible_count and cjk_count / visible_count >= 0.03:
                    layout_regions = _pdf_text_regions(pdf_page)
                else:
                    layout_regions = _layout_text_regions(layout_text)
                    if not layout_regions:
                        layout_regions = _pdf_text_regions(pdf_page)
                paragraphs = []
            else:
                layout_regions = []
                paragraphs = _split_plain_text(text)
                if text.strip() and not paragraphs:
                    paragraphs = [text.strip()]

            if _should_extract_pdf_tables(text):
                try:
                    pdf_page = pdf_page or plumber_pdf.pages[page_number - 1]
                    tables = pdf_page.find_tables()
                except Exception as exc:  # noqa: BLE001 - table extraction is best effort.
                    warnings.append(
                        f"Page {page_number} tables could not be parsed: {exc}"
                    )
                    tables = []
                for table in tables:
                    role_map = _table_role_map(pdf_page, table)
                    if not any(role == "target" for role in role_map.values()):
                        continue
                    seen_cells: set[str] = set()
                    for row_index, row in enumerate(table.rows):
                        for column_index, column in enumerate(table.columns):
                            table_role = role_map.get((row_index, column_index))
                            if table_role not in {"target", "progress"}:
                                continue
                            cell_bbox = (
                                column.bbox[0],
                                row.bbox[1],
                                column.bbox[2],
                                row.bbox[3],
                            )
                            try:
                                cell_text = " ".join(
                                    (
                                        pdf_page.crop(cell_bbox).extract_text() or ""
                                    ).split()
                                )
                            except Exception:  # noqa: BLE001, S112 - skip malformed cell.
                                continue
                            normalized_cell = re.sub(r"\s+", " ", cell_text).casefold()
                            if (
                                len(cell_text) < 8
                                or len(cell_text) > 1500
                                or normalized_cell in seen_cells
                            ):
                                continue
                            seen_cells.add(normalized_cell)
                            paragraph_index += 1
                            blocks.append(
                                DocumentBlock(
                                    block_id=f"b{paragraph_index:05d}",
                                    text=cell_text,
                                    paragraph_index=paragraph_index,
                                    page_number=page_number,
                                    section=current_section,
                                    is_heading=False,
                                    source_type="table",
                                    table_role=table_role,
                                )
                            )

            for region in layout_regions:
                paragraph_index += 1
                is_heading = _heading_like(region.text)
                if is_heading:
                    current_section = region.text.lstrip("#").strip()
                blocks.append(
                    DocumentBlock(
                        block_id=f"b{paragraph_index:05d}",
                        text=region.text,
                        paragraph_index=paragraph_index,
                        page_number=page_number,
                        section=current_section,
                        is_heading=is_heading,
                        source_type="paragraph",
                        table_role=(
                            None
                            if region.table_role == "neutral"
                            else region.table_role
                        ),
                    )
                )

            for paragraph in paragraphs:
                paragraph_index += 1
                is_heading = _heading_like(paragraph)
                if is_heading:
                    current_section = paragraph.lstrip("#").strip()
                blocks.append(
                    DocumentBlock(
                        block_id=f"b{paragraph_index:05d}",
                        text=paragraph,
                        paragraph_index=paragraph_index,
                        page_number=page_number,
                        section=current_section,
                        is_heading=is_heading,
                    )
                )

    if not blocks:
        raise ValueError(
            "No text layer was found in the PDF. v0.3.0 does not perform OCR."
        )
    return (blocks if used_layout_blocks else _stitch_page_fragments(blocks)), warnings


def _page_needs_layout(text: str) -> bool:
    target_cue = re.search(
        r"\b(?:targets?|commitments?|commits?|pledges?|goals?|aims?\s+to|"
        r"plans?\s+to|will|by\s+(?:19|20)\d{2}|each\s+year|annually)\b|"
        r"(?:目标|承诺|计划|将在|将于|到\s*(?:19|20)\d{2}|每年|年度|定期)",
        text,
        re.IGNORECASE,
    )
    topic_cue = re.search(
        r"\b(?:climate|carbon|emission|energy|water|waste|recycl|supplier|"
        r"employee|workforce|board|diversity|privacy|safety|biodiversity)\b|"
        r"(?:气候|碳|排放|能源|水|废弃物|回收|供应商|员工|董事|女性|隐私|安全|"
        r"生物多样性)",
        text,
        re.IGNORECASE,
    )
    return bool(target_cue and topic_cue)


def _should_extract_pdf_tables(text: str) -> bool:
    signals = (
        text.count("%")
        + text.count("％")
        + len(re.findall(r"目标|target|goals?", text, re.IGNORECASE))
    )
    explicit_header = re.search(
        r"(?:管理目标|目标及承诺)[^\n]{0,100}(?:管理进展|进展)|"
        r"(?:goals?|targets?)[^\n]{0,100}progress",
        text,
        re.IGNORECASE,
    )
    return signals >= 3 and bool(explicit_header)


def _table_role_map(page, table) -> dict[tuple[int, int], str]:
    texts = _table_cell_texts(page, table)
    if not texts:
        return {}

    first_row = texts.get(0, {})
    goal_columns = {
        column
        for column, text in first_row.items()
        if "管理目标" in text or "目标及承诺" in text
    }
    progress_columns = {
        column
        for column, text in first_row.items()
        if "管理进展" in text or text.strip() == "进展"
    }
    if goal_columns and progress_columns:
        return {
            (row_index, column_index): (
                "target"
                if column_index in goal_columns
                else "progress"
                if column_index in progress_columns
                else "neutral"
            )
            for row_index, row in texts.items()
            for column_index in row
        }

    row_labels: dict[int, str] = {}
    for row_index, cells in texts.items():
        first_cell = cells[min(cells)].strip()
        if re.fullmatch(
            r"(?:目标|目标及承诺|阶段目标|关键目标|承诺|"
            r"goal|goals|target|targets)",
            first_cell,
            re.IGNORECASE,
        ):
            row_labels[row_index] = "target"
        elif re.fullmatch(
            r"(?:\d{4}\s*年?\s*)?(?:进展|progress|status)",
            first_cell,
            re.IGNORECASE,
        ):
            row_labels[row_index] = "progress"
    if {"target", "progress"}.issubset(row_labels.values()):
        ordered_labels = sorted(row_labels.items())
        result: dict[tuple[int, int], str] = {}
        active_role = "neutral"
        label_index = 0
        for row_index in sorted(texts):
            while (
                label_index < len(ordered_labels)
                and ordered_labels[label_index][0] <= row_index
            ):
                active_role = ordered_labels[label_index][1]
                label_index += 1
            for column_index in texts[row_index]:
                result[(row_index, column_index)] = active_role
        return result
    return {
        (row_index, column_index): "neutral"
        for row_index, row in texts.items()
        for column_index in row
    }


def _join_tokens(parts: list[str]) -> str:
    result = ""
    for part in parts:
        clean = part.strip()
        if not clean:
            continue
        if not result:
            result = clean
            continue
        separator = (
            ""
            if re.search(r"[\u3400-\u9fff]$", result)
            or re.match(r"^[\u3400-\u9fff]", clean)
            else " "
        )
        result = f"{result}{separator}{clean}"
    return result


def _layout_text_regions(text: str) -> list[_TextRegion]:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    segments: list[_TextRegion] = []
    for line_index, line in enumerate(lines):
        start = 0
        for gap in re.finditer(r"\s{8,}", line):
            _append_layout_segment(segments, line, line_index, start, gap.start())
            start = gap.end()
        _append_layout_segment(segments, line, line_index, start, len(line))

    if not any(region.text for region in segments):
        return []

    _assign_layout_table_roles(segments)
    merged: list[_TextRegion] = []
    for segment in sorted(
        segments,
        key=lambda item: (item.top, item.x0, item.bottom),
    ):
        candidates = [
            region
            for region in merged[-120:]
            if 0 <= segment.top - region.bottom <= 1
            and _horizontal_overlap(region, segment) >= 0.30
            and not _layout_label_role(region.text)
            and not _layout_label_role(segment.text)
            and (
                segment.table_role == region.table_role
                or "neutral" in {segment.table_role, region.table_role}
            )
        ]
        if not candidates:
            merged.append(segment)
            continue
        target = min(
            candidates,
            key=lambda item: (
                abs(segment.top - item.bottom),
                abs(segment.x0 - item.x0),
            ),
        )
        target.x0 = min(target.x0, segment.x0)
        target.top = min(target.top, segment.top)
        target.x1 = max(target.x1, segment.x1)
        target.bottom = max(target.bottom, segment.bottom)
        target.text = _join_tokens([target.text, segment.text])

    page_height = max(1, len(lines))
    regions = [
        region
        for region in merged
        if region.text
        and not (region.top < 2 and len(region.text) > 100)
        and not (region.top > page_height * 0.94 and len(region.text) > 180)
    ]
    _assign_layout_table_roles(regions)
    return sorted(regions, key=lambda item: (round(item.top, 1), item.x0))


def _append_layout_segment(
    segments: list[_TextRegion],
    line: str,
    line_index: int,
    start: int,
    end: int,
) -> None:
    raw = line[start:end]
    clean = " ".join(raw.split())
    if not clean:
        return
    leading = len(raw) - len(raw.lstrip())
    trailing = len(raw) - len(raw.rstrip())
    segments.append(
        _TextRegion(
            x0=float(start + leading),
            top=float(line_index),
            x1=float(max(start + leading + 1, end - trailing)),
            bottom=float(line_index + 1),
            text=clean,
        )
    )


def _pdf_text_regions(page) -> list[_TextRegion]:
    try:
        words = page.extract_words(
            x_tolerance=2,
            y_tolerance=3,
            keep_blank_chars=False,
            use_text_flow=False,
        )
    except Exception:  # noqa: BLE001 - layout parsing is best effort.
        return []

    visual_lines: list[list[dict]] = []
    for word in sorted(words, key=lambda item: (float(item["top"]), float(item["x0"]))):
        target_line = None
        for line in reversed(visual_lines[-8:]):
            if abs(float(line[0]["top"]) - float(word["top"])) <= 3:
                target_line = line
                break
        if target_line is None:
            visual_lines.append([word])
        else:
            target_line.append(word)

    segments: list[_TextRegion] = []
    for line in visual_lines:
        current: list[dict] = []
        for word in sorted(line, key=lambda item: float(item["x0"])):
            if current and float(word["x0"]) - float(current[-1]["x1"]) > 12:
                segments.append(_segment_region(current))
                current = []
            current.append(word)
        if current:
            segments.append(_segment_region(current))

    _assign_layout_table_roles(segments)
    merged: list[_TextRegion] = []
    for segment in sorted(
        segments,
        key=lambda item: (item.top, item.x0, item.bottom),
    ):
        candidates = [
            region
            for region in merged[-120:]
            if 0 <= segment.top - region.bottom <= 12
            and _horizontal_overlap(region, segment) >= 0.30
            and not _layout_label_role(region.text)
            and not _layout_label_role(segment.text)
            and (
                segment.table_role == region.table_role
                or "neutral" in {segment.table_role, region.table_role}
            )
        ]
        if not candidates:
            merged.append(segment)
            continue
        target = min(
            candidates,
            key=lambda item: (
                abs(segment.top - item.bottom),
                abs(segment.x0 - item.x0),
            ),
        )
        target.x0 = min(target.x0, segment.x0)
        target.top = min(target.top, segment.top)
        target.x1 = max(target.x1, segment.x1)
        target.bottom = max(target.bottom, segment.bottom)
        target.text = _join_tokens([target.text, segment.text])

    page_height = float(getattr(page, "height", 0) or 0)
    regions = [
        region
        for region in merged
        if region.text
        and not (region.top < 50 and len(region.text) > 100)
        and not (page_height and region.top > page_height * 0.92)
    ]
    _assign_layout_table_roles(regions)
    return sorted(regions, key=lambda item: (round(item.top, 1), item.x0))


def _segment_region(words: list[dict]) -> _TextRegion:
    ordered = sorted(words, key=lambda item: float(item["x0"]))
    return _TextRegion(
        x0=min(float(item["x0"]) for item in ordered),
        top=min(float(item["top"]) for item in ordered),
        x1=max(float(item["x1"]) for item in ordered),
        bottom=max(float(item["bottom"]) for item in ordered),
        text=_join_tokens([str(item["text"]) for item in ordered]),
    )


def _horizontal_overlap(left: _TextRegion, right: _TextRegion) -> float:
    overlap = min(left.x1, right.x1) - max(left.x0, right.x0)
    if overlap <= 0:
        return 0.0
    smaller_width = max(1.0, min(left.x1 - left.x0, right.x1 - right.x0))
    return overlap / smaller_width


def _layout_label_role(text: str) -> str | None:
    normalized = text.strip().casefold()
    if re.fullmatch(
        r"(?:目标|目标及承诺|阶段目标|关键目标|承诺|"
        r"goal|goals|target|targets)",
        normalized,
    ):
        return "target"
    if re.fullmatch(
        r"(?:\d{4}\s*年?\s*)?(?:进展|progress|status)",
        normalized,
    ):
        return "progress"
    return None


def _assign_layout_table_roles(regions: list[_TextRegion]) -> None:
    labels = [
        (region.center_y, role)
        for region in regions
        if (role := _layout_label_role(region.text)) is not None
    ]
    if {role for _, role in labels} != {"target", "progress"} or len(labels) < 2:
        return
    for region in regions:
        if _layout_label_role(region.text) is not None:
            continue
        nearest_center, nearest_role = min(
            labels,
            key=lambda item: abs(item[0] - region.center_y),
        )
        if abs(nearest_center - region.center_y) <= 60:
            region.table_role = nearest_role


def _table_cell_texts(page, table) -> dict[int, dict[int, str]]:
    result: dict[int, dict[int, str]] = {}
    for row_index, row in enumerate(table.rows):
        for column_index, column in enumerate(table.columns):
            bbox = (
                column.bbox[0],
                row.bbox[1],
                column.bbox[2],
                row.bbox[3],
            )
            try:
                text = " ".join((page.crop(bbox).extract_text() or "").split())
            except Exception:  # noqa: BLE001, S112 - skip malformed cell.
                continue
            if text:
                result.setdefault(row_index, {})[column_index] = text
    return result


def _stitch_page_fragments(blocks: list[DocumentBlock]) -> list[DocumentBlock]:
    """Join a paragraph that continues across a PDF page boundary."""
    stitched: list[DocumentBlock] = []
    for block in blocks:
        previous_index = next(
            (
                index
                for index in range(len(stitched) - 1, -1, -1)
                if not stitched[index].is_heading
            ),
            None,
        )
        previous = stitched[previous_index] if previous_index is not None else None
        if (
            previous is not None
            and not block.is_heading
            and previous.source_type == "paragraph"
            and block.source_type == "paragraph"
            and previous.page_number is not None
            and block.page_number == previous.page_number + 1
            and not re.search(r"[。！？!?；;：:.]\s*$", previous.text)
        ):
            separator = "" if re.search(r"[\u4e00-\u9fff]$", previous.text) else " "
            previous.text = f"{previous.text}{separator}{block.text}".strip()
            continue
        stitched.append(block)
    return stitched


def _ingest_docx(data: bytes) -> tuple[list[DocumentBlock], list[str]]:
    document = Document(io.BytesIO(data))
    blocks: list[DocumentBlock] = []
    warnings: list[str] = []
    paragraph_index = 0
    current_section: str | None = None

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue
        paragraph_index += 1
        style_name = paragraph.style.name if paragraph.style else ""
        is_heading = style_name.lower().startswith(
            ("heading", "标题")
        ) or _heading_like(text)
        if is_heading:
            current_section = text.lstrip("#").strip()
        blocks.append(
            DocumentBlock(
                block_id=f"b{paragraph_index:05d}",
                text=text,
                paragraph_index=paragraph_index,
                section=current_section,
                is_heading=is_heading,
            )
        )

    for table_index, table in enumerate(document.tables, start=1):
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if not cells:
                continue
            paragraph_index += 1
            text = " | ".join(cells)
            blocks.append(
                DocumentBlock(
                    block_id=f"b{paragraph_index:05d}",
                    text=text,
                    paragraph_index=paragraph_index,
                    section=current_section or f"Table {table_index}",
                    is_heading=False,
                )
            )

    if not blocks:
        raise ValueError(
            "The DOCX file contains no readable paragraphs or table cells."
        )
    return blocks, warnings


def _ingest_text(data: bytes) -> tuple[list[DocumentBlock], list[str]]:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = data.decode("gb18030")
    paragraphs = _split_plain_text(text)
    blocks: list[DocumentBlock] = []
    paragraph_index = 0
    current_section: str | None = None
    for paragraph_index, paragraph in enumerate(paragraphs, start=1):
        is_heading = _heading_like(paragraph)
        if is_heading:
            current_section = paragraph.lstrip("#").strip()
        blocks.append(
            DocumentBlock(
                block_id=f"b{paragraph_index:05d}",
                text=paragraph,
                paragraph_index=paragraph_index,
                section=current_section,
                is_heading=is_heading,
            )
        )
    if not blocks:
        raise ValueError("The text file is empty.")
    return blocks, []


def ingest_bytes(data: bytes, filename: str) -> IngestedDocument:
    if not data:
        raise ValueError("The uploaded file is empty.")
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(
            f"Unsupported file type '{extension or '(none)'}'. Supported: {supported}"
        )

    try:
        if extension == ".pdf":
            blocks, warnings = _ingest_pdf(data)
        elif extension == ".docx":
            blocks, warnings = _ingest_docx(data)
        else:
            blocks, warnings = _ingest_text(data)
    except ValueError:
        raise
    except (
        BadZipFile,
        KeyError,
        PDFSyntaxError,
        PackageNotFoundError,
        PdfReadError,
        XMLSyntaxError,
    ) as exc:
        label = extension.lstrip(".").upper()
        raise ValueError(f"The {label} file could not be parsed.") from exc

    return IngestedDocument(
        filename=filename,
        extension=extension,
        sha256=hashlib.sha256(data).hexdigest(),
        character_count=sum(len(block.text) for block in blocks),
        blocks=blocks,
        warnings=warnings,
    )


def ingest_path(path: str | Path) -> IngestedDocument:
    file_path = Path(path)
    return ingest_bytes(file_path.read_bytes(), file_path.name)
