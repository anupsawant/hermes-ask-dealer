---
name: pdf
description: "PDFs: design reports, read, merge, fill forms, OCR."
version: 2.0.0
author: Nous Research
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pdf, documents, reports, design, forms, ocr, text-extraction, reportlab, pypdf, pdfplumber, pymupdf, marker]
    category: productivity
    related_skills: [docx, xlsx, powerpoint]
---

# PDF Skill

Create designed PDF reports (themes, KPI cards with red/yellow/green status, charts, callouts, tables), build and fill AcroForm forms, extract text/tables/metadata, merge/split/rotate/watermark/stamp pages, export page images, manage metadata and attachments, and encrypt/decrypt — using pypdf, reportlab, and pdfplumber. It does not do pixel-perfect HTML-to-PDF rendering. Two capabilities live in references/ (read the matching file before those tasks):

- **Scanned/image-only PDFs and OCR** (pymupdf fast path, marker-pdf quality path): `references/ocr-extraction.md`
- **Editing text inside an existing PDF via natural-language prompts** (nano-pdf CLI): `references/nano-pdf-editing.md`

## When to Use

- Generate a report, summary, invoice, or multi-page document as a PDF that looks designed, not just valid.
- Produce any report, summary, guide, proposal, or one-pager that should look professionally formatted. Start from `templates/general_report.json`.
- Produce a recurring metrics report (daily/weekly/monthly) where problem areas must stand out. Start from `templates/department_daily_report.json`.
- Build a fillable AcroForm (text/checkbox/radio/dropdown) from a JSON spec, linting the layout first.
- Pull text, tables (JSON/CSV), metadata, or form-field values out of a PDF.
- Merge, split, rotate, watermark, stamp, bookmark, or compress PDFs; export pages as PNG; set metadata; add/extract attachments.
- Fill or flatten forms; encrypt or decrypt with passwords.
- NOT for scanned PDFs (use `references/ocr-extraction.md`) and NOT for exact HTML/CSS rendering (use a headless browser).

## Prerequisites

- Python 3.10+ with `pypdf`, `reportlab`, `pdfplumber`: `python -m pip install pypdf reportlab pdfplumber`
- Page rendering (needed to inspect every report): `python -m pip install pypdfium2`, or poppler's `pdftoppm` on PATH. Without either, `--preview` reports `{"rendered": false, "missing": [...]}` instead of failing.
- Each helper script checks imports lazily and prints an install hint if a dependency is missing.

## How to Run

All helpers live in `scripts/` and are argparse CLIs — run them with the `terminal` tool; every one supports `--help`. They read/write JSON as UTF-8, print JSON results to stdout, and exit non-zero on failure.

```bash
python scripts/pdf_create.py spec.json -o out.pdf --preview prev/   # build + render every page to PNG
python scripts/pdf_make_form.py formspec.json -o form.pdf           # build fillable AcroForm
python scripts/pdf_form_layout.py formspec.json                     # lint form layout BEFORE building
python scripts/pdf_form_layout.py formspec.json --render-overlay boxes.png [--pdf form.pdf]
python scripts/pdf_read.py doc.pdf --text                           # per-page text (JSON)
python scripts/pdf_read.py doc.pdf --tables --csv-dir t/            # tables to JSON + CSV files
python scripts/pdf_read.py doc.pdf --meta                           # metadata, sizes, encrypted/scanned flags
python scripts/pdf_read.py form.pdf --fields                        # form fields: name, type, value
python scripts/pdf_merge.py a.pdf b.pdf -o merged.pdf [--bookmarks]
python scripts/pdf_split.py doc.pdf --pages 1-3,7 -o part.pdf [--rotate 90]
python scripts/pdf_fill_form.py form.pdf --fields-json values.json -o filled.pdf [--flatten]
python scripts/pdf_secure.py doc.pdf --encrypt -o enc.pdf --user-password your-password
python scripts/pdf_secure.py enc.pdf --decrypt -o dec.pdf --password your-password
python scripts/pdf_watermark.py doc.pdf --stamp mark.pdf -o stamped.pdf [--under]
python scripts/pdf_stamp.py doc.pdf -o out.pdf --text "DRAFT" --x 150 --y 400 --font-size 60 --rotation 45
python scripts/pdf_stamp.py doc.pdf -o out.pdf --image sig.png --x 400 --y 60 --width 120
python scripts/pdf_page_image.py doc.pdf --pages 1-3 --dpi 150 --out-dir imgs/
python scripts/pdf_meta.py doc.pdf --set-meta --title "T" --author "A" -o out.pdf
python scripts/pdf_meta.py doc.pdf --attach data.csv -o out.pdf
python scripts/pdf_meta.py doc.pdf --list-attachments | --extract-attachments dir/
```

## Quick Reference

| Task | Tool | Command / API |
|---|---|---|
| Create designed doc / report | reportlab platypus | `pdf_create.py spec.json -o out.pdf --preview prev/` |
| Start a general report or document | template | copy `templates/general_report.json` |
| Start a department KPI report | template | copy `templates/department_daily_report.json` |
| Build / lint fillable form | reportlab acroForm | `pdf_make_form.py`, `pdf_form_layout.py` |
| Per-page text / tables / metadata | pdfplumber, pypdf | `pdf_read.py f.pdf --text / --tables / --meta` |
| Merge / split / rotate | pypdf | `pdf_merge.py`, `pdf_split.py` |
| List / fill / flatten form | pypdf | `pdf_read.py --fields`, `pdf_fill_form.py` |
| Encrypt / decrypt (AES-256) | pypdf | `pdf_secure.py --encrypt/--decrypt` |
| Watermark / stamp | pypdf + reportlab | `pdf_watermark.py`, `pdf_stamp.py` |
| Pages to PNG | pypdfium2 or pdftoppm | `pdf_page_image.py f.pdf --out-dir imgs/` |
| Metadata, attachments | pypdf | `pdf_meta.py` |

### Spec elements for `pdf_create.py`

Top-level keys: `title`, `author`, `page_size` (`A4`/`letter`), `theme`, `footer_text`, `page_numbers`, `elements`. Themes: `corporate` (default), `modern`, `classic` (plain pre-2.0 look).

| Element | Fields | Use for |
|---|---|---|
| `title` | `text`, `subtitle`, `meta` | document opener with accent rule |
| `heading` | `text`, `level` 1-3 | sections (kept on the same page as what follows) |
| `paragraph` | `text` (`<b>`/`<i>` allowed) | body text |
| `bullets` | `items`, `numbered` | lists; open each item with a `<b>bold lead-in:</b>` when items are parallel |
| `callout` | `tone` info/success/warning/danger, `title`, `text` | takeaways, warnings, actions |
| `metrics` | `columns`, `sort_by_status`, `items[{label,value,status,note}]` | KPI cards; status red/yellow/green/neutral shown as colour AND word; `sort_by_status` puts red first |
| `chart` | `kind` bar/line/pie, `title`, `categories`, `series[{name,values}]`, `height`, `labels` | trends and comparisons |
| `table` | `rows`, `header`, `col_widths` (relative weights), `status_col` | data; cells wrap, columns fit the page; cells reading red/yellow/green get coloured |
| `image` | `path`, `width` | pictures |
| `spacer` / `pagebreak` | `height` | spacing, forced page break |

## Procedure

1. **Inspect first.** Run `pdf_read.py file.pdf --meta`. Check `encrypted` (decrypt first with `pdf_secure.py --decrypt`) and `likely_scanned_pages`. For image-only pages export PNGs with `pdf_page_image.py --dpi 300` and follow `references/ocr-extraction.md` — never report empty text as "no content".
2. **Create a document.**
   1. Decide the audience and what must be seen first. Put the most important items at the top; for status reports lead with red items.
   2. Write the spec with `write_file` to a unique file name (for example include the date or a counter) — `write_file` refuses to overwrite a file it has not read. For a department KPI report, copy `templates/department_daily_report.json` and replace every placeholder.
   3. Build with `pdf_create.py spec.json -o out.pdf --preview prev/`.
   4. **Inspect every page (required).** Open each PNG listed under `preview.files` with `vision_analyze` and check for clipped or overlapping text, awkward page breaks, unreadable tables or charts, wrong colours, and missing sections. Fix the spec and rebuild until clean.
   5. Only then report completion. If `preview.rendered` is false, install `pypdfium2` with `terminal` and rerun; if rendering is impossible, tell the user the layout was not visually checked.
3. **Design rules.**
   - Default structure for a general document: `title`, a short Summary (conclusion first) with one `callout` for the key takeaway, sections as level-1 headings, `bullets` instead of runs of one-line paragraphs, a `table` for comparisons across attributes, and a closing Next steps or Assumptions block when useful. Do not pad to a page count.
   - One accent colour family; use red/yellow/green only for status, always with a word as well (greyscale printing).
   - Use a chart only when comparing numbers over time or categories; label units; use a table when exact values matter.
   - A callout is for one important point, not decoration. Keep sections short; do not pad to fill pages.
   - Never invent numbers. Use values the user or a data source supplied; mark missing data as missing. Remove every "SAMPLE DATA" marker and placeholder before a report is sent to anyone.
4. **Extract.** `--text` gives per-page strings; `--tables` gives row arrays and optional CSV files. Read results with `read_file`; never eyeball a binary PDF directly.
5. **Manipulate.** `pdf_merge.py` concatenates (optionally one bookmark per source); `pdf_split.py` handles 1-based page ranges (`1-3,5,9-`), 90-degree rotation, and `--compress`. Watermark with a one-page stamp PDF via `pdf_watermark.py`; use `pdf_stamp.py` for text or image stamps at explicit coordinates. Write to a new output path; keep the original.
6. **Build forms.** Write one form-spec JSON (fields with `label_box`/`entry_box` in PDF points — see `references/forms.md`), lint with `pdf_form_layout.py` and fix every reported problem, review the `--render-overlay` PNG with `vision_analyze`, build with `pdf_make_form.py`, confirm with `pdf_read.py --fields`.
7. **Fill forms.** List fields (`--fields`) for exact names and types, write `{"FieldName": "value"}` UTF-8 JSON with `write_file` (checkboxes take `true`/`false`; radio/choice values must match the export options), run `pdf_fill_form.py`, re-read with `--fields`.
8. **Metadata and attachments.** `pdf_meta.py --set-meta` writes Title/Author/Subject/Keywords; `--attach`/`--list-attachments`/`--extract-attachments` round-trip embedded files.
9. **Secure.** Encrypt with distinct user/owner passwords (AES-256). `--decrypt` writes an unencrypted copy only when the user supplied the password.

## Pitfalls

- **Skipping the page check.** "File opens and has N pages" is not verification: clipped tables and overlapping text pass that test. Inspect every rendered page.
- **Overwrite refusal.** `write_file` will not replace an existing spec it has not read; use a fresh file name per build.
- **Fonts are Latin-only.** Built-in Helvetica has no glyphs for other scripts; those characters render blank. Verify visually.
- **Long tables.** Tables up to 15 rows are kept on one page; longer ones split and repeat the header row.
- **Placeholder data.** Template values are zeros and dashes on purpose. A chart of all zeros is a sign nothing was filled in.
- **Scanned PDFs**: empty `extract_text()` means no text layer. Route to `references/ocr-extraction.md`; do not fabricate text.
- **Flattening limits**: `--flatten` can drop or misrender rich text, custom appearance streams, and some radio groups. Verify visually.
- **NeedAppearances**: some viewers ignore the flag after filling; flatten if display fidelity matters.
- **Compression**: `--compress` only deflates content streams; 0-20% savings, nothing for image-heavy files.
- **Permission flags don't enforce**: owner-password bits (no-print, no-copy) are requests; only the user password gates content. Never present them as security.
- **Table extraction is heuristic**: borderless or merged-cell tables may need `table_settings` tuning or manual cleanup.
- **Page indexing**: helper CLIs take 1-based pages; pypdf APIs are 0-based. The scripts convert — do not double-convert.
- **Rotated stamp text**: pdfplumber scrambles rotated glyphs; verify rotated stamps with a rendered image.
- **Radio groups**: reportlab needs two or more `radio()` widgets per group and the slashed export value on fill (`"/red"`); see `references/forms.md`.
- **Metadata scope**: `pdf_meta.py` writes classic DocInfo only; embedded XMP may disagree.
- **PDF/A is out of scope**: use Ghostscript via `terminal` and validate with veraPDF; never claim conformance unvalidated.
- Rotation must be a multiple of 90; decrypt encrypted inputs before any other operation; never try to bypass a password.

## Verification

- After `pdf_create.py`: every page listed in `preview.files` was opened with `vision_analyze` and looked right; `pdf_read.py out.pdf --meta` shows the expected `page_count`; expected headings and key values appear in `--text`.
- After merge/split: `--meta` confirms `page_count` and per-page `rotation`.
- After extraction: output is non-empty and a known string or cell matches.
- Form design loop: `pdf_form_layout.py` exits 0; review the overlay PNG; after building, `--fields` lists every field with the right type; after filling, values match exactly (including non-ASCII).
- After stamping or flattening: render the page and inspect it (`pdf_page_image.py`).
- After metadata/attachment edits: `--meta` / `--list-attachments`; byte-compare an extracted attachment.
- After encrypt: `--meta` shows `"encrypted": true` and opening without a password fails; after decrypt, text matches the original.
- State honestly what was and was not visually checked.
