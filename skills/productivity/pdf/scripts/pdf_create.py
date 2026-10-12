#!/usr/bin/env python3
"""Create a PDF from a JSON spec using reportlab platypus.

Spec format (UTF-8 JSON):
{
  "title": "Example Report",
  "author": "example-author",
  "page_size": "A4",            // or "letter" (default: A4)
  "page_numbers": true,          // default true
  "theme": "corporate",          // "corporate" (default) | "modern" | "classic" (plain, pre-2.0 look)
  "footer_text": "Example Co",   // left footer text (default: title)
  "elements": [
    {"type": "title", "text": "Daily Service Report", "subtitle": "Subaru Service", "meta": "7 Oct 2026"},
    {"type": "heading", "text": "Section 1", "level": 1},
    {"type": "paragraph", "text": "Body text..."},
    {"type": "bullets", "items": ["<b>Lead-in:</b> point one", "point two"], "numbered": false},
    {"type": "callout", "tone": "warning", "title": "Watch", "text": "Efficiency is below target."},
    {"type": "metrics", "columns": 3, "sort_by_status": true, "items": [
        {"label": "Effective labor rate", "value": "$142", "status": "red", "note": "target $150"},
        {"label": "Gross", "value": "$18.4k", "status": "green"}]},
    {"type": "chart", "kind": "bar", "title": "Hours by day", "categories": ["Mon", "Tue"],
     "series": [{"name": "Sold", "values": [32, 41]}, {"name": "Available", "values": [40, 40]}]},
    {"type": "table", "rows": [["H1", "H2"], ["a", "b"]], "header": true,
     "col_widths": [1, 3],         // optional relative column weights
     "status_col": 1},             // optional: colour cells in this column that read red/yellow/green
    {"type": "image", "path": "chart.png", "width": 400},
    {"type": "spacer", "height": 12},
    {"type": "pagebreak"}
  ]
}

Tones: info | success | warning | danger.  Statuses: red | yellow | green | neutral.
Chart kinds: bar | line | pie (pie uses the first series only).

`--preview DIR` renders every page to PNG after building so the result can be inspected.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

_MIN_COL_WEIGHT = 8
_MAX_COL_WEIGHT = 60
_KEEP_TOGETHER_ROWS = 8
_STATUS_ORDER = {"red": 0, "yellow": 1, "green": 2, "neutral": 3}

# classic = the pre-2.0 plain look (sample stylesheet, grey grid); others are opt-in palettes.
_THEMES = {
    "corporate": {
        "primary": "#1F3A5F", "accent": "#2E6FA7", "text": "#1B1F24", "muted": "#6B7280",
        "header_bg": "#1F3A5F", "header_fg": "#FFFFFF", "zebra": "#F3F6FA", "rule": "#C9D3E0",
        "series": ["#2E6FA7", "#E08A1E", "#3A9D6E", "#8A5CB8", "#C0392B", "#6B7280"],
    },
    "modern": {
        "primary": "#111827", "accent": "#0F766E", "text": "#111827", "muted": "#6B7280",
        "header_bg": "#0F766E", "header_fg": "#FFFFFF", "zebra": "#F5F7F7", "rule": "#D1D5DB",
        "series": ["#0F766E", "#F59E0B", "#2563EB", "#9333EA", "#DC2626", "#6B7280"],
    },
    "classic": None,
}
_STATUS = {  # solid colour, text colour on that solid colour
    "red": ("#C0392B", "#FFFFFF"),
    "yellow": ("#F2C230", "#1B1F24"),
    "green": ("#1E8E5A", "#FFFFFF"),
    "neutral": ("#6B7280", "#FFFFFF"),
}
_STATUS_TEXT = {"red": "#C0392B", "yellow": "#8A6A00", "green": "#1E8E5A", "neutral": "#4B5563"}  # on a tinted card
_TONES = {"info": "#2E6FA7", "success": "#1E8E5A", "warning": "#D98E04", "danger": "#C0392B"}


def _reconfigure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def _column_widths(rows: list, available: float, weights: list | None) -> list[float]:
    """Column widths in points that sum to `available`.

    Without explicit `weights`, each column is weighted by its longest cell, clamped so one long
    description cannot squeeze a short label column to nothing (or push the table off the page).
    """
    from reportlab.pdfbase.pdfmetrics import stringWidth

    ncols = max(len(row) for row in rows)
    if weights and len(weights) == ncols and all(float(w) > 0 for w in weights):
        shares = [float(w) for w in weights]
    else:
        shares = [
            min(max(max((len(str(row[i])) for row in rows if i < len(row)), default=0), _MIN_COL_WEIGHT), _MAX_COL_WEIGHT)
            for i in range(ncols)
        ]
    # Never narrower than the longest single word (+ cell padding), so words are not split mid-word.
    floors = [
        max((stringWidth(word, "Helvetica-Bold", 9) for row in rows if i < len(row) for word in str(row[i]).split()), default=0)
        + 12
        for i in range(ncols)
    ]
    widths = [available * share / sum(shares) for share in shares]
    pinned = {i for i in range(ncols) if widths[i] < floors[i]}
    if pinned and len(pinned) < ncols:
        free_share = sum(shares[i] for i in range(ncols) if i not in pinned)
        free_width = available - sum(floors[i] for i in pinned)
        widths = [floors[i] if i in pinned else free_width * shares[i] / free_share for i in range(ncols)]
    return widths


def _tint(hex_color: str, amount: float):
    """Blend a colour toward white (amount 0 = original, 1 = white)."""
    from reportlab.lib import colors

    base = colors.HexColor(hex_color)
    return colors.Color(
        base.red + (1 - base.red) * amount, base.green + (1 - base.green) * amount, base.blue + (1 - base.blue) * amount
    )


_BARE_AMPERSAND = re.compile(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)")
_NON_TAG_LT = re.compile(r"<(?!/?(?:b|i|u|br|strong|em|font|super|sub|strike)\b[^<>]*>)")


def _para(text, style):
    """Paragraph that keeps inline markup (<b>, <i>, <br/>) but treats a stray & or < as text.

    ReportLab does not reject "R&D" or "a < b", it silently rewrites them ("R&D;"), so they are escaped first.
    """
    from reportlab.platypus import Paragraph

    safe = _NON_TAG_LT.sub("&lt;", _BARE_AMPERSAND.sub("&amp;", str(text)))
    try:
        return Paragraph(safe, style)
    except Exception:  # malformed tag nesting: show the text literally rather than fail the build
        return Paragraph(escape(str(text)), style)


def _cell(text, style):
    """Table cells are always plain text: escaped, with newlines kept."""
    from reportlab.platypus import Paragraph

    return Paragraph(escape(str(text)).replace("\n", "<br/>"), style)


def _build_styles(theme: dict | None):
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

    styles = getSampleStyleSheet()
    if theme is not None:
        text, primary = colors.HexColor(theme["text"]), colors.HexColor(theme["primary"])
        styles["BodyText"].textColor = text
        styles["BodyText"].leading = 14
        for level, size in ((1, 20), (2, 15), (3, 12)):
            heading = styles[f"Heading{level}"]
            heading.textColor = primary
            heading.fontSize = size
            heading.leading = size + 4
            heading.spaceBefore = 14 if level > 1 else 6
            heading.spaceAfter = 6
    cell = ParagraphStyle("TableCell", parent=styles["BodyText"], fontSize=9, leading=11)
    head = ParagraphStyle(
        "TableHead", parent=cell, fontName="Helvetica-Bold",
        textColor=colors.HexColor(theme["header_fg"]) if theme else colors.black,
    )
    styles.add(cell)
    styles.add(head)
    styles.add(ParagraphStyle("Title2", parent=styles["Title"], alignment=0, fontSize=26, leading=30, spaceAfter=4,
                              textColor=primary if theme else colors.black))
    styles.add(ParagraphStyle("Subtitle2", parent=styles["BodyText"], fontSize=13, leading=17,
                              textColor=colors.HexColor(theme["muted"]) if theme else colors.grey))
    styles.add(ParagraphStyle("Meta", parent=styles["BodyText"], fontSize=9, leading=12, textColor=colors.grey))
    return styles


def _table(el: dict, doc_width: float, styles, theme: dict | None):
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle

    rows = el.get("rows", [])
    has_header = el.get("header", True)
    status_col = el.get("status_col")
    cells = []
    for r, row in enumerate(rows):
        out = []
        for c, cell in enumerate(row):
            style = styles["TableHead"] if has_header and r == 0 else styles["TableCell"]
            if status_col == c and not (has_header and r == 0) and str(cell).strip().lower() in _STATUS:
                from reportlab.lib.styles import ParagraphStyle

                style = ParagraphStyle(
                    f"Status{r}_{c}", parent=styles["TableCell"], fontName="Helvetica-Bold",
                    textColor=colors.HexColor(_STATUS[str(cell).strip().lower()][1]),
                )
            out.append(_cell(cell, style))
        cells.append(out)
    table = Table(
        cells,
        colWidths=_column_widths(rows, doc_width, el.get("col_widths")),
        repeatRows=1 if has_header else 0,
    )
    grid = colors.HexColor(theme["rule"]) if theme else colors.grey
    style = [("GRID", (0, 0), (-1, -1), 0.5, grid), ("VALIGN", (0, 0), (-1, -1), "TOP")]
    if has_header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(theme["header_bg"]) if theme else colors.lightgrey))
    if theme and len(rows) > 2:
        style.append(("ROWBACKGROUNDS", (0, 1 if has_header else 0), (-1, -1), [colors.white, colors.HexColor(theme["zebra"])]))
    if status_col is not None:
        for r, row in enumerate(rows):
            if has_header and r == 0:
                continue
            if status_col < len(row) and str(row[status_col]).strip().lower() in _STATUS:
                style.append(("BACKGROUND", (status_col, r), (status_col, r),
                              colors.HexColor(_STATUS[str(row[status_col]).strip().lower()][0])))
    table.setStyle(TableStyle(style))
    return table


def _callout(el: dict, doc_width: float, styles):
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Table, TableStyle

    tone = _TONES.get(str(el.get("tone", "info")).lower(), _TONES["info"])
    body = ParagraphStyle("CalloutBody", parent=styles["BodyText"], fontSize=10, leading=13)
    title = ParagraphStyle("CalloutTitle", parent=body, fontName="Helvetica-Bold", textColor=colors.HexColor(tone))
    content = []
    if el.get("title"):
        content.append(_para(el["title"], title))
    content.append(_para(el.get("text", ""), body))
    box = Table([[content]], colWidths=[doc_width])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _tint(tone, 0.9)),
        ("LINEBEFORE", (0, 0), (0, -1), 4, colors.HexColor(tone)),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return box


def _metrics(el: dict, doc_width: float, styles):
    """Grid of KPI cards. Status is shown as a word as well as a colour, so it survives greyscale printing."""
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Table, TableStyle

    items = list(el.get("items", []))
    if not items:
        return None
    if el.get("sort_by_status", False):
        items.sort(key=lambda i: _STATUS_ORDER.get(str(i.get("status", "neutral")).lower(), 3))  # stable: red first
    columns = max(1, int(el.get("columns", 3)))
    base = styles["BodyText"]
    label_style = ParagraphStyle("MetricLabel", parent=base, fontSize=8.5, leading=10, textColor=colors.HexColor("#4B5563"))
    value_style = ParagraphStyle("MetricValue", parent=base, fontName="Helvetica-Bold", fontSize=18, leading=22)
    note_style = ParagraphStyle("MetricNote", parent=base, fontSize=8, leading=10, textColor=colors.HexColor("#6B7280"))
    rows, style = [], [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LINEAFTER", (0, 0), (-1, -1), 6, colors.white), ("LINEBELOW", (0, 0), (-1, -1), 6, colors.white),
    ]
    for index, item in enumerate(items):
        status = str(item.get("status", "neutral")).lower()
        solid, _ = _STATUS.get(status, _STATUS["neutral"])
        status_style = ParagraphStyle(
            f"MetricStatus{index}", parent=note_style, fontName="Helvetica-Bold",
            textColor=colors.HexColor(_STATUS_TEXT.get(status, _STATUS_TEXT["neutral"])),
        )
        content = [_cell(item.get("label", ""), label_style), _cell(item.get("value", ""), value_style)]
        if status in _STATUS and status != "neutral":
            content.append(_cell(status.upper(), status_style))
        if item.get("note"):
            content.append(_cell(item["note"], note_style))
        r, c = divmod(index, columns)
        if c == 0:
            rows.append([""] * columns)
        rows[r][c] = content
        style += [("BACKGROUND", (c, r), (c, r), _tint(solid, 0.9)), ("LINEBEFORE", (c, r), (c, r), 4, colors.HexColor(solid))]
    table = Table(rows, colWidths=[doc_width / columns] * columns)
    table.setStyle(TableStyle(style))
    return table


def _chart(el: dict, doc_width: float, theme: dict | None):
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.legends import Legend
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.shapes import Drawing, String
    from reportlab.graphics.widgets.markers import makeMarker
    from reportlab.lib import colors

    palette = [colors.HexColor(c) for c in (theme or _THEMES["corporate"])["series"]]
    kind = str(el.get("kind", "bar")).lower()
    categories = [str(c) for c in el.get("categories", [])]
    series = el.get("series", [])
    if not series:
        return None
    width = min(float(el.get("width", doc_width)), doc_width)
    height = float(el.get("height", 200))
    drawing = Drawing(width, height)
    top = 8
    if el.get("title"):
        drawing.add(String(width / 2, height - 14, str(el["title"]), fontName="Helvetica-Bold", fontSize=11, textAnchor="middle"))
        top = 26
    legend_pairs = [(palette[i % len(palette)], str(s.get("name", f"Series {i + 1}"))) for i, s in enumerate(series)]
    if kind == "pie":
        values = [float(v) for v in series[0].get("values", [])]
        chart = Pie()
        chart.x, chart.y = width * 0.28, 18
        chart.width = chart.height = max(40.0, height - top - 36)
        chart.data = values
        chart.labels = [f"{categories[i] if i < len(categories) else ''} ({v:g})" for i, v in enumerate(values)]
        chart.sideLabels = 1
        chart.slices.strokeWidth = 0.5
        chart.slices.strokeColor = colors.white
        chart.slices.fontName = "Helvetica"
        chart.slices.fontSize = 8
        for i in range(len(values)):
            chart.slices[i].fillColor = palette[i % len(palette)]
        drawing.add(chart)
        return drawing
    multi = len(series) > 1
    chart = HorizontalLineChart() if kind == "line" else VerticalBarChart()
    chart.x, chart.y = 44, 26
    chart.width = width - 60
    chart.height = height - top - (44 if multi else 14) - 12
    chart.data = [[float(v) for v in s.get("values", [])] for s in series]
    chart.categoryAxis.categoryNames = categories
    for axis in (chart.categoryAxis, chart.valueAxis):
        axis.labels.fontName = "Helvetica"
        axis.labels.fontSize = 8
    chart.valueAxis.visibleGrid = 1
    chart.valueAxis.gridStrokeColor = colors.HexColor("#E5E7EB")
    if all(v >= 0 for s in chart.data for v in s):
        chart.valueAxis.valueMin = 0
        if not any(v for s in chart.data for v in s):
            chart.valueAxis.valueMax = 1  # all-zero placeholder data would otherwise get a 0.01 scale
    if kind == "line":
        for i in range(len(series)):
            chart.lines[i].strokeColor = palette[i % len(palette)]
            chart.lines[i].strokeWidth = 2
            chart.lines[i].symbol = makeMarker("FilledCircle")
            chart.lines[i].symbol.size = 4
            chart.lines[i].symbol.fillColor = palette[i % len(palette)]
    else:
        chart.groupSpacing = 8
        chart.bars.strokeColor = None
        for i in range(len(series)):
            chart.bars[i].fillColor = palette[i % len(palette)]
        if el.get("labels", True) and len(categories) * len(series) <= 24:
            chart.barLabelFormat = "%g"
            chart.barLabels.nudge = 7
            chart.barLabels.fontName = "Helvetica"
            chart.barLabels.fontSize = 7
    drawing.add(chart)
    if multi:
        legend = Legend()
        legend.x, legend.y = 70, height - top - 2
        legend.fontName = "Helvetica"
        legend.fontSize = 8
        legend.dx = legend.dy = 8
        legend.alignment = "right"
        legend.columnMaximum = 1
        legend.deltax = 70
        legend.dxTextSpace = 5
        legend.colorNamePairs = legend_pairs
        drawing.add(legend)
    return drawing


def build_pdf(spec: dict, out_path: str) -> int:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, letter
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            CondPageBreak,
            HRFlowable,
            Image,
            KeepTogether,
            ListFlowable,
            ListItem,
            PageBreak,
            SimpleDocTemplate,
            Spacer,
        )
    except ImportError:
        print("Missing dependency: install with 'python3 -m pip install reportlab'", file=sys.stderr)
        return 2

    theme_name = str(spec.get("theme", "corporate")).lower()
    if theme_name not in _THEMES:
        print(f"Warning: unknown theme {theme_name!r}, using corporate", file=sys.stderr)
        theme_name = "corporate"
    theme = _THEMES[theme_name]

    page_size = letter if str(spec.get("page_size", "A4")).lower() == "letter" else A4
    margin = 0.75 * inch if theme else inch
    doc = SimpleDocTemplate(
        out_path,
        pagesize=page_size,
        title=spec.get("title", ""),
        author=spec.get("author", ""),
        leftMargin=margin, rightMargin=margin, topMargin=margin, bottomMargin=margin + 0.15 * inch,
    )
    styles = _build_styles(theme)
    story = []
    held: list = []  # heading flowables waiting to be grouped with the block that follows them

    def add(flowable, *, keep: bool = False) -> None:
        """Append a block; a pending heading moves to the next page together with it (never stranded)."""
        if held:
            story.append(KeepTogether([*held, flowable]))
            held.clear()
        else:
            story.append(KeepTogether(flowable) if keep else flowable)

    for el in spec.get("elements", []):
        etype = el.get("type")
        if etype == "title":
            story.append(_para(el.get("text", ""), styles["Title2"]))
            if el.get("subtitle"):
                story.append(_para(el["subtitle"], styles["Subtitle2"]))
            if el.get("meta"):
                story.append(_para(el["meta"], styles["Meta"]))
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor(theme["accent"] if theme else "#999999")))
            story.append(Spacer(1, 12))
        elif etype == "heading":
            level = min(max(int(el.get("level", 1)), 1), 3)
            held.append(_para(el.get("text", ""), styles[f"Heading{level}"]))
            if theme and level == 1:
                held.extend([HRFlowable(width="100%", thickness=0.75, color=colors.HexColor(theme["rule"])), Spacer(1, 6)])
        elif etype == "paragraph":
            add(_para(el.get("text", ""), styles["BodyText"]))
            story.append(Spacer(1, 6))
        elif etype == "bullets":
            items = [ListItem(_para(text, styles["BodyText"]), leftIndent=18) for text in el.get("items", [])]
            if items:
                numbered = bool(el.get("numbered"))
                add(
                    ListFlowable(
                        items, bulletType="1" if numbered else "bullet", bulletFormat="%s." if numbered else None,
                        leftIndent=18, bulletFontSize=10 if numbered else 12,
                    ),
                    keep=True,
                )
                story.append(Spacer(1, 6))
        elif etype == "callout":
            add(_callout(el, doc.width, styles), keep=True)
            story.append(Spacer(1, 10))
        elif etype == "metrics":
            block = _metrics(el, doc.width, styles)
            if block is not None:
                add(block, keep=True)
                story.append(Spacer(1, 10))
        elif etype == "chart":
            drawing = _chart(el, doc.width, theme)
            if drawing is not None:
                add(drawing, keep=True)
                story.append(Spacer(1, 10))
        elif etype == "table":
            if not el.get("rows"):
                continue
            table = _table(el, doc.width, styles, theme)
            if len(el["rows"]) <= _KEEP_TOGETHER_ROWS:
                add(table, keep=True)  # a short table moves to the next page whole
            else:
                # a long table may split (header repeats); only require room for its heading and first rows
                story.append(CondPageBreak(120))
                story.extend(held)
                held.clear()
                story.append(table)
            story.append(Spacer(1, 10))
        elif etype == "image":
            kwargs = {}
            if el.get("width"):
                kwargs["width"] = float(el["width"])
            if el.get("height"):
                kwargs["height"] = float(el["height"])
            img = Image(el["path"], **kwargs)
            if "width" in kwargs and "height" not in kwargs:
                # keep aspect ratio
                ratio = img.imageHeight / img.imageWidth
                img.drawWidth = kwargs["width"]
                img.drawHeight = kwargs["width"] * ratio
            add(img, keep=True)
            story.append(Spacer(1, 10))
        elif etype == "spacer":
            story.append(Spacer(1, float(el.get("height", 12))))
        elif etype == "pagebreak":
            story.append(PageBreak())
        else:
            print(f"Warning: unknown element type {etype!r}, skipped", file=sys.stderr)

    story.extend(held)  # a trailing heading with nothing after it
    footer_text = str(spec.get("footer_text", spec.get("title", "")) or "")

    def draw_footer(canvas, doc_):
        canvas.saveState()
        if theme:
            canvas.setStrokeColor(colors.HexColor(theme["rule"]))
            canvas.setLineWidth(0.5)
            canvas.line(margin, 0.62 * inch, page_size[0] - margin, 0.62 * inch)
        canvas.setFont("Helvetica", 8.5)
        canvas.setFillColor(colors.HexColor(theme["muted"]) if theme else colors.black)
        if theme and footer_text:
            canvas.drawString(margin, 0.45 * inch, footer_text[:90])
        if spec.get("page_numbers", True):
            if theme:
                canvas.drawRightString(page_size[0] - margin, 0.45 * inch, f"Page {doc_.page}")
            else:
                canvas.drawCentredString(page_size[0] / 2.0, 0.5 * inch, f"Page {doc_.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
    return 0


def _render_preview(pdf_path: str, preview_dir: str, dpi: int) -> dict:
    """Rasterize every page so the caller can look at the result; never raises."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import _raster
        from pypdf import PdfReader

        if not _raster.available_backends():
            return {"rendered": False, "missing": _raster.missing_hints()}
        page_count = len(PdfReader(pdf_path).pages)
        out_dir = Path(preview_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        files = []
        for pageno in range(1, page_count + 1):
            img = _raster.rasterize_page(pdf_path, pageno, dpi=dpi)
            if img is None:
                return {"rendered": False, "missing": _raster.missing_hints()}
            target = out_dir / f"preview{pageno:03d}.png"
            img.save(target)
            files.append(str(target))
        return {"rendered": True, "dpi": dpi, "files": files}
    except Exception as exc:  # preview is a convenience; the PDF is already written
        return {"rendered": False, "error": str(exc)}


def main() -> int:
    _reconfigure_stdio()
    parser = argparse.ArgumentParser(description="Create a PDF from a JSON spec (reportlab).")
    parser.add_argument("spec", help="Path to UTF-8 JSON spec file")
    parser.add_argument("-o", "--output", required=True, help="Output PDF path")
    parser.add_argument("--preview", metavar="DIR", help="Also render every page to PNG in DIR for inspection")
    parser.add_argument("--preview-dpi", type=int, default=90, help="Preview DPI (default 90)")
    args = parser.parse_args()
    with open(args.spec, encoding="utf-8") as fh:
        spec = json.load(fh)
    code = build_pdf(spec, args.output)
    if code != 0:
        return code
    result = {"output": args.output, "elements": len(spec.get("elements", []))}
    if args.preview:
        result["preview"] = _render_preview(args.output, args.preview, args.preview_dpi)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
