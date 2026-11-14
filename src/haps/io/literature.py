"""Literature intake tools (task cards T-LIT.01 and T-LIT.03).

These tools work on the team's literature folder on the shared drive
(``fydp-haps-data/literature/``) and write small text outputs into the
repository's ``literature/`` folder. They never modify the drive files.

Commands (run from the repository root, ``haps`` environment active)::

    python -m haps.io.literature index  --src "<drive>/literature" --out literature
    python -m haps.io.literature copies --src "<drive>/literature" --out "<drive>/literature/text_copies"
    python -m haps.io.literature leads  --src "<drive>/literature" --out literature/ai_leads.csv \
                                        --index literature/index.csv
    python -m haps.io.literature gaps   --src "<drive>/literature" --out literature/gap_register.csv

``index``  writes ``index.csv`` (one row per file, with SHA-256, PDF title,
           DOI and arXiv identifiers found on the first pages) and
           ``duplicates.csv`` (files that are the same by hash, DOI or title).
``copies`` writes plain-text copies (Markdown or CSV) of every AI-derived
           file into the drive's literature/text_copies/ folder, so people and
           agents can read them (kept out of Git: the repository is public).
``leads``  lists every DOI, URL, arXiv ID and OpenAlex ID that the AI-derived
           files mention. These are leads to check, never citations.
``gaps``   extracts the "Research Gaps" entries of the Scientific Watch
           Report PDFs into the gap register, all with status UNVERIFIED.

Folder names are mapped to categories by ``FOLDER_CATEGORIES``; both the
recommended layout (literature/README.md) and the original folder names
are recognised. Files in unrecognised folders are indexed as ``unknown``.

Requires PyMuPDF (``pymupdf``) for PDFs and ``python-docx`` for Word files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
import unicodedata
from collections import defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import asdict, dataclass, fields
from pathlib import Path

# --------------------------------------------------------------------------
# Folder -> (category, credibility tier). Tiers follow PLAN.md section 3.8:
# A/B are decided per paper during T-LIT.01; C = AI-generated, never cited.
# --------------------------------------------------------------------------
FOLDER_CATEGORIES: dict[str, tuple[str, str]] = {
    # recommended layout
    "papers": ("paper", "TBD"),
    "ai_derived/reviews": ("ai_review", "C"),
    "ai_derived/watch_reports": ("ai_watch_report", "C"),
    "ai_derived/source_lists": ("ai_source_list", "C"),
    "ai_derived/extraction_tables": ("ai_extraction_table", "C"),
    "team_lists": ("team_list", "list"),
    "_not_for_repo": ("excluded", "excluded"),
    # original folder names (before reorganisation)
    "PDFs": ("paper", "TBD"),
    "Literature Review": ("ai_review", "C"),
    "Scientific Watch Report": ("ai_watch_report", "C"),
    "Sources in csv files": ("ai_source_list", "C"),
    "Sources in text files": ("ai_source_list", "C"),
    "Sources in md files": ("team_list", "list"),
}

AI_CATEGORIES = {"ai_review", "ai_watch_report", "ai_source_list", "ai_extraction_table"}
SKIP_NAMES = {"desktop.ini", "Thumbs.db", ".DS_Store"}
# Generated folders inside the drive's literature/ that must not be indexed or copied again.
SKIP_DIRS = {"text_copies", "_duplicates"}

DOI_RE = re.compile(r"\b10\.\d{4,9}/[^\s\"'<>|\]\[)(,;]+", re.IGNORECASE)
ARXIV_RE = re.compile(r"\barXiv[:\s]*(\d{4}\.\d{4,5})(v\d+)?", re.IGNORECASE)
ARXIV_URL_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})(v\d+)?", re.IGNORECASE)
OPENALEX_RE = re.compile(r"\bopenalex[_:/ ]*(W\d{6,12})\b", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s<>\"'\])]+", re.IGNORECASE)
GAP_HEAD_RE = re.compile(r"^\s*\[(HIGH|MEDIUM|LOW)\]\s*(.+)$")
BULLET_RE = re.compile(r"^\s*[■•▪●]\s*(.+)$")
# PyMuPDF renders the report's square bullet glyph as an indented capital "I".
PDF_BULLET_RE = re.compile(r"^\s{2,}I\s+(.+)$")
# Shadow-library links and link lists are kept out of the repository.
SHADOW_RE = re.compile(r"(?i)https?://[^\s)\]]*(annas-archive|libgen|sci-hub|z-lib|zlibrary)[^\s)\]]*")
EXCLUDED_NAME_RE = re.compile(r"(?i)\banna'?s\b")


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------
def sha256_of(path: Path, chunk: int = 1 << 20) -> str:
    """Return the SHA-256 hex digest of a file, read in 1 MiB chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(chunk):
            digest.update(block)
    return digest.hexdigest()


def normalise_title(title: str) -> str:
    """Lower-case, accent-free, alphanumeric-only form of a title for matching."""
    text = unicodedata.normalize("NFKD", title or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", text.casefold())


def clean_doi(raw: str) -> str:
    """Strip trailing punctuation and URL noise from a DOI match; lower-case it."""
    doi = raw.strip().rstrip(".,;:)]}>\"'")
    doi = re.sub(r"(?i)(\.pdf|/full|/abstract|/epdf)$", "", doi)
    return doi.lower()


def classify(rel_path: Path) -> tuple[str, str]:
    """Map a path relative to the literature root to (category, tier)."""
    if EXCLUDED_NAME_RE.search(rel_path.name):
        return FOLDER_CATEGORIES["_not_for_repo"]
    parts = rel_path.parts[:-1]
    for depth in range(len(parts), 0, -1):  # longest folder prefix wins
        key = "/".join(parts[:depth])
        if key in FOLDER_CATEGORIES:
            return FOLDER_CATEGORIES[key]
    return ("unknown", "TBD")


def iter_files(root: Path) -> Iterator[Path]:
    """Yield every regular file under root, skipping editor lock files and OS files."""
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name.startswith("~$") or path.name in SKIP_NAMES:
            continue
        if SKIP_DIRS.intersection(path.relative_to(root).parts[:-1]):
            continue
        yield path


def write_csv(path: Path, rows: Iterable[dict], header: list[str]) -> int:
    """Write rows to a UTF-8 CSV with the given header; return the row count."""
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


# --------------------------------------------------------------------------
# Text extraction
# --------------------------------------------------------------------------
def pdf_text(path: Path, max_pages: int | None = None) -> str:
    """Extract text from a PDF with PyMuPDF (empty string for scanned pages)."""
    import pymupdf  # imported lazily so the package imports without it

    with pymupdf.open(path) as doc:
        pages = range(doc.page_count if max_pages is None else min(max_pages, doc.page_count))
        return "\n".join(doc[i].get_text("text") for i in pages)


def _xml_text(element) -> str:
    """Concatenate all text, tab and break nodes under a WordprocessingML element."""
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    parts: list[str] = []
    for node in element.iter():
        if node.tag == ns + "t" and node.text:
            parts.append(node.text)
        elif node.tag in (ns + "tab", ns + "br", ns + "cr"):
            parts.append(" ")
    return "".join(parts)


def _looks_like_heading(para, text: str) -> bool:
    """True for a short, fully bold paragraph without final punctuation (a heading
    typed in a Normal style, as Jenni AI exports do)."""
    runs = [r for r in para.runs if r.text.strip()]
    return (
        0 < len(text) <= 120
        and not text.endswith((".", ":", ";", ","))
        and bool(runs)
        and all(r.bold for r in runs)
    )


def docx_markdown(path: Path) -> str:
    """Convert a .docx to simple Markdown: headings, paragraphs and tables."""
    import docx  # python-docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    document = docx.Document(str(path))
    lines: list[str] = []
    for block in document.element.body.iterchildren():
        tag = block.tag.rsplit("}", 1)[-1]
        if tag == "p":
            para = Paragraph(block, document)
            # Read every w:t node, so text inside hyperlinks, fields and content
            # controls (where AI tools put in-text citations) is kept.
            text = _xml_text(block).strip()
            if not text:
                continue
            style = (para.style.name or "").lower() if para.style is not None else ""
            level = re.search(r"heading\s*(\d)", style)
            if level:
                lines.append("#" * min(int(level.group(1)) + 1, 6) + " " + text)
            elif style == "title":
                lines.append("# " + text)
            elif "list" in style:
                lines.append("- " + text)
            elif _looks_like_heading(para, text):
                lines.append("### " + text)  # bold short line used as a heading
            else:
                lines.append(text)
            lines.append("")
        elif tag == "tbl":
            table = Table(block, document)
            for i, row in enumerate(table.rows):
                cells = [_xml_text(c._tc).strip().replace("\n", " ").replace("|", "/") for c in row.cells]
                lines.append("| " + " | ".join(cells) + " |")
                if i == 0:
                    lines.append("|" + "---|" * len(cells))
            lines.append("")
    return "\n".join(lines).strip() + "\n"


def read_text(path: Path) -> str:
    """Return readable text for any supported file type."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return pdf_text(path)
    if suffix == ".docx":
        return docx_markdown(path)
    return path.read_text(encoding="utf-8-sig", errors="replace")


# --------------------------------------------------------------------------
# index: one row per file, plus duplicate detection
# --------------------------------------------------------------------------
@dataclass
class IndexRow:
    file_id: str
    path: str
    category: str
    tier: str
    format: str
    bytes: int
    sha256: str
    pages: str = ""
    title: str = ""
    authors: str = ""
    year: str = ""
    venue: str = ""
    doi: str = ""
    arxiv: str = ""
    type: str = ""
    topic_tags: str = ""
    citekey: str = ""
    duplicate_of: str = ""
    status: str = "AUTO"
    notes: str = ""


INDEX_HEADER = [f.name for f in fields(IndexRow)]


def pdf_facts(path: Path) -> dict[str, str]:
    """Pages, title, DOI and arXiv ID from PDF metadata and its first two pages."""
    import pymupdf

    facts = {"pages": "", "title": "", "doi": "", "arxiv": "", "notes": ""}
    try:
        with pymupdf.open(path) as doc:
            facts["pages"] = str(doc.page_count)
            meta_title = (doc.metadata or {}).get("title", "") or ""
            text = "\n".join(doc[i].get_text("text") for i in range(min(2, doc.page_count)))
    except (RuntimeError, ValueError) as exc:  # corrupt/encrypted PDF (FileDataError)
        facts["notes"] = f"could not open: {exc.__class__.__name__}"
        return facts
    if len(text.strip()) < 200:
        facts["notes"] = "little or no text layer: probably scanned, needs OCR"
    if len(meta_title) > 15 and not re.search(r"(?i)untitled|microsoft word|\.docx?$|^doi", meta_title):
        facts["title"] = meta_title.strip()
    if match := DOI_RE.search(text):
        facts["doi"] = clean_doi(match.group(0))
    if match := ARXIV_RE.search(text) or ARXIV_URL_RE.search(text):
        facts["arxiv"] = match.group(1)
    return facts


def build_index(src: Path) -> list[IndexRow]:
    """Scan the literature folder and return one IndexRow per file."""
    rows: list[IndexRow] = []
    counters: dict[str, int] = defaultdict(int)
    prefix = {"paper": "P", "ai_review": "R", "ai_watch_report": "W", "ai_source_list": "S",
              "ai_extraction_table": "X", "team_list": "T", "excluded": "E", "unknown": "U"}
    for path in iter_files(src):
        rel = path.relative_to(src)
        category, tier = classify(rel)
        counters[category] += 1
        row = IndexRow(
            file_id=f"{prefix[category]}{counters[category]:03d}",
            path=rel.as_posix(),
            category=category,
            tier=tier,
            format=path.suffix.lower().lstrip("."),
            bytes=path.stat().st_size,
            sha256=sha256_of(path),
        )
        if category == "excluded":
            row.notes = "kept off the repository; see literature/README.md"
        elif row.format == "pdf":
            for key, value in pdf_facts(path).items():
                setattr(row, key, value)
        if category in AI_CATEGORIES:
            row.type = "AI-generated"
        rows.append(row)
        print(f"  indexed {row.file_id} {rel.as_posix()}", file=sys.stderr)
    return rows


def find_duplicates(rows: list[IndexRow]) -> list[dict[str, str]]:
    """Group files that are identical (hash) or the same work (DOI, arXiv ID, title)."""
    keys: dict[tuple[str, str], list[IndexRow]] = defaultdict(list)
    for row in rows:
        if row.category in {"excluded"}:
            continue
        keys[("sha256", row.sha256)].append(row)
        if row.doi:
            keys[("doi", row.doi)].append(row)
        if row.arxiv:
            keys[("arxiv", row.arxiv)].append(row)
        norm = normalise_title(row.title)
        if len(norm) >= 25:
            keys[("title", norm)].append(row)

    out: list[dict[str, str]] = []
    seen: set[tuple[str, ...]] = set()
    for (basis, value), group in keys.items():
        ids = tuple(sorted({r.file_id for r in group}))
        if len(ids) < 2 or ids in seen:
            continue
        seen.add(ids)
        keep = min(group, key=lambda r: (-r.bytes, r.path))  # suggest the largest file
        for r in group:
            if r.file_id != keep.file_id and not r.duplicate_of:
                r.duplicate_of = keep.file_id
        out.append({
            "basis": basis,
            "value": value[:80],
            "file_ids": " ".join(ids),
            "paths": " | ".join(sorted({r.path for r in group})),
            "suggested_keep": keep.file_id,
            "decision": "",
        })
    return out


# --------------------------------------------------------------------------
# copies: readable text copies of AI-derived files
# --------------------------------------------------------------------------
COPY_SUBFOLDER = {
    "ai_review": "reviews",
    "ai_watch_report": "watch_reports",
    "ai_source_list": "source_lists",
    "ai_extraction_table": "extraction_tables",
    "team_list": "team_lists",
}


def slugify(name: str) -> str:
    """File-system-safe, lower-case slug for an output file name."""
    text = unicodedata.normalize("NFKD", name)
    text = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return text[:90] or "file"


def make_copies(src: Path, out: Path) -> list[Path]:
    """Write a Markdown (or CSV) copy of each AI-derived and team-list file."""
    written: list[Path] = []
    for path in iter_files(src):
        rel = path.relative_to(src)
        category, _ = classify(rel)
        if category not in COPY_SUBFOLDER:
            continue
        sub = out / COPY_SUBFOLDER[category]
        sub.mkdir(parents=True, exist_ok=True)
        stem = slugify(path.stem)
        digest = sha256_of(path)
        if path.suffix.lower() == ".csv":
            target = sub / f"{stem}.csv"
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            target.write_text(text.replace("\r\n", "\n"), encoding="utf-8")
        else:
            target = sub / f"{stem}.md"
            body = SHADOW_RE.sub("[link removed: shadow library]", read_text(path))
            trust = (
                "Tier C (AI-generated)" if category in AI_CATEGORIES
                else "Link list: each linked item is tiered on its own"
            )
            banner = (
                f"<!-- TEXT COPY. Original: literature/{rel.as_posix()} (shared drive)\n"
                f"     sha256: {digest}\n"
                f"     Category: {category}. {trust}. See literature/SOURCES_INDEX.md.\n"
                f"     Never cite this file. Never copy its text into reports.\n"
                f"     Trace every claim to a paper first: see literature/README.md. -->\n\n"
            )
            target.write_text(banner + body, encoding="utf-8")
        written.append(target)
        print(f"  copied {rel.as_posix()} -> {target}", file=sys.stderr)
    return written


# --------------------------------------------------------------------------
# leads: identifiers mentioned in AI-derived files
# --------------------------------------------------------------------------
LEADS_HEADER = ["lead_id", "kind", "identifier", "source_file", "line", "context",
                "in_library", "exists", "checked_by", "date", "notes"]


def extract_leads(text: str) -> Iterator[tuple[str, str, int, str]]:
    """Yield (kind, identifier, line_number, context) for every identifier in text."""
    for number, line in enumerate(text.splitlines(), start=1):
        found: set[tuple[str, str]] = set()
        for match in DOI_RE.finditer(line):
            found.add(("doi", clean_doi(match.group(0))))
        for match in ARXIV_URL_RE.finditer(line):
            found.add(("arxiv", match.group(1)))
        for match in OPENALEX_RE.finditer(line):
            found.add(("openalex", match.group(1).upper()))
        for match in URL_RE.finditer(line):
            url = match.group(0).rstrip(".,;:")
            if SHADOW_RE.match(url) or "doi.org/" in url.lower() or "arxiv.org/" in url.lower():
                continue  # already captured as DOI or arXiv ID
            found.add(("url", url))
        context = re.sub(r"\s+", " ", line).strip()[:100]
        for kind, ident in sorted(found):
            yield kind, ident, number, context


def library_keys(index_csv: Path | None) -> dict[tuple[str, str], str]:
    """Map ("doi"|"arxiv", identifier) -> file_id from an existing index.csv."""
    keys: dict[tuple[str, str], str] = {}
    if index_csv is None or not index_csv.is_file():
        return keys
    with index_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("category") != "paper":
                continue
            if row.get("doi"):
                keys[("doi", row["doi"].lower())] = row["file_id"]
            if row.get("arxiv"):
                keys[("arxiv", row["arxiv"])] = row["file_id"]
    return keys


def build_leads(src: Path, index_csv: Path | None = None) -> list[dict[str, str]]:
    """Collect unique leads from AI-derived and team-list files. If index.csv is
    given, DOI and arXiv leads already in the library get their file_id."""
    library = library_keys(index_csv)
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for path in iter_files(src):
        rel = path.relative_to(src)
        category, _ = classify(rel)
        if category not in COPY_SUBFOLDER:
            continue
        for kind, ident, line, context in extract_leads(read_text(path)):
            key = (kind, ident.lower())
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "lead_id": f"L{len(rows) + 1:04d}",
                "kind": kind,
                "identifier": ident,
                "source_file": rel.as_posix(),
                "line": str(line),
                "context": context,
                "in_library": library.get((kind, ident.lower()), library.get((kind, ident), "")),
            })
    return rows


# --------------------------------------------------------------------------
# gaps: Research Gaps sections of the Scientific Watch Report PDFs
# --------------------------------------------------------------------------
GAP_HEADER = ["gap_id", "priority_ai", "claim", "ai_suggested_actions", "source_file",
              "status", "supporting_papers", "contradicting_papers", "relevance_to_project",
              "checked_by", "date", "notes"]


@dataclass
class Gap:
    priority_ai: str
    claim: str
    ai_suggested_actions: str


def parse_watch_report_gaps(text: str) -> list[Gap]:
    """Parse '[HIGH] claim' entries and their bullets between 'Research Gaps' and
    'Future Perspectives'. Wrapped lines are joined; page footers are dropped."""
    lines = text.splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip().lower() == "research gaps")
    except StopIteration:
        return []
    gaps: list[Gap] = []
    current: Gap | None = None
    target = "claim"
    for raw in lines[start + 1:]:
        line = raw.strip()
        if line.lower().startswith("future perspectives"):
            break
        if not line or "Scientific Watch Report agent" in line:
            continue
        if head := GAP_HEAD_RE.match(line):
            current = Gap(head.group(1), head.group(2).strip(), "")
            gaps.append(current)
            target = "claim"
        elif current is None:
            continue
        elif bullet := BULLET_RE.match(line) or PDF_BULLET_RE.match(raw):
            sep = "; " if current.ai_suggested_actions else ""
            current.ai_suggested_actions += sep + bullet.group(1).strip()
            target = "actions"
        elif target == "claim":
            current.claim += " " + line
        else:
            current.ai_suggested_actions += " " + line
    return gaps


def build_gaps(src: Path) -> list[dict[str, str]]:
    """Gap-register rows from every watch-report PDF under src."""
    rows: list[dict[str, str]] = []
    for path in iter_files(src):
        rel = path.relative_to(src)
        category, _ = classify(rel)
        if category != "ai_watch_report" or path.suffix.lower() != ".pdf":
            continue
        import pymupdf

        with pymupdf.open(path) as doc:
            text = "\n".join(page.get_text("text") for page in doc)
        for gap in parse_watch_report_gaps(text):
            rows.append({
                "gap_id": f"G{len(rows) + 1:03d}",
                **asdict(gap),
                "source_file": rel.as_posix(),
                "status": "UNVERIFIED",
            })
    return rows


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m haps.io.literature", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name, helptext in {
        "index": "write index.csv and duplicates.csv",
        "copies": "write text copies of AI-derived files",
        "leads": "write ai_leads.csv",
        "gaps": "write gap_register.csv from watch reports",
    }.items():
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--src", type=Path, required=True, help="literature folder on the shared drive")
        p.add_argument("--out", type=Path, required=True, help="output folder or file")
        p.add_argument("--force", action="store_true",
                       help="overwrite existing output files (manual edits in them are lost)")
        if name == "leads":
            p.add_argument("--index", type=Path, default=None,
                           help="existing literature/index.csv, to mark leads already in the library")
    args = parser.parse_args(argv)

    src: Path = args.src.expanduser().resolve()
    if not src.is_dir():
        parser.error(f"--src is not a folder: {src}")

    # index, leads and gaps write CSVs that people later fill in: never overwrite silently.
    protected = {
        "index": [args.out / "index.csv", args.out / "duplicates.csv"],
        "leads": [args.out],
        "gaps": [args.out],
    }.get(args.command, [])
    existing = [str(p) for p in protected if p.exists()]
    if existing and not args.force:
        parser.error("would overwrite " + ", ".join(existing)
                     + " (may contain manual edits). Use --force, or choose another --out.")

    if args.command == "index":
        rows = build_index(src)
        dups = find_duplicates(rows)
        n = write_csv(args.out / "index.csv", (asdict(r) for r in rows), INDEX_HEADER)
        d = write_csv(args.out / "duplicates.csv", dups,
                      ["basis", "value", "file_ids", "paths", "suggested_keep", "decision"])
        print(f"index.csv: {n} files; duplicates.csv: {d} groups")
    elif args.command == "copies":
        print(f"{len(make_copies(src, args.out))} text copies written to {args.out}")
    elif args.command == "leads":
        leads = build_leads(src, args.index)
        n = write_csv(args.out, leads, LEADS_HEADER)
        hits = sum(1 for r in leads if r.get("in_library"))
        print(f"ai_leads.csv: {n} unique identifiers, {hits} already in the library")
    elif args.command == "gaps":
        n = write_csv(args.out, build_gaps(src), GAP_HEADER)
        print(f"gap_register.csv: {n} gaps (all UNVERIFIED)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
