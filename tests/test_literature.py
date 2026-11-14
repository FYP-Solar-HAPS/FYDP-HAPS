"""Unit tests for haps.io.literature (no real literature files needed)."""

from pathlib import Path

from haps.io.literature import (
    IndexRow,
    classify,
    clean_doi,
    extract_leads,
    find_duplicates,
    normalise_title,
    parse_watch_report_gaps,
)


def test_normalise_title_ignores_case_accents_and_punctuation():
    assert normalise_title("Énergie: Solar-Powered UAVs!") == normalise_title("energie solar powered uavs")


def test_clean_doi_strips_trailing_noise():
    assert clean_doi("10.3390/Electronics9010179.") == "10.3390/electronics9010179"
    assert clean_doi("10.2514/1.C035566/full") == "10.2514/1.c035566"


def test_classify_recognises_old_and_new_folders_and_exclusions():
    assert classify(Path("PDFs/x.pdf")) == ("paper", "TBD")
    assert classify(Path("papers/x.pdf")) == ("paper", "TBD")
    assert classify(Path("Scientific Watch Report/r.pdf")) == ("ai_watch_report", "C")
    assert classify(Path("ai_derived/reviews/r.docx")) == ("ai_review", "C")
    assert classify(Path("Sources in text files/Annas sources.txt"))[0] == "excluded"
    assert classify(Path("elsewhere/x.pdf"))[0] == "unknown"


def test_gap_parser_joins_wrapped_lines_and_collects_bullets():
    text = (
        "Research Gaps\n"
        "[HIGH] Limited research on long-term environmental effects on\n"
        "solar UAV durability.\n"
        "    I Conduct longitudinal studies.\n"
        "    I Build stress-test models.\n"
        "Scientific Watch Report agent ReAct+Reflexion -- topic -- Page 2\n"
        "[MEDIUM] Sparse work on small solar UAVs.\n"
        "  \u25a0 Build prototypes.\n"
        "Future Perspectives\n"
        "[LOW] must not be parsed\n"
    )
    gaps = parse_watch_report_gaps(text)
    assert [g.priority_ai for g in gaps] == ["HIGH", "MEDIUM"]
    assert gaps[0].claim.endswith("solar UAV durability.")
    assert gaps[0].ai_suggested_actions == "Conduct longitudinal studies.; Build stress-test models."
    assert gaps[1].ai_suggested_actions == "Build prototypes."


def test_leads_find_identifiers_and_drop_shadow_library_links():
    text = (
        "See https://doi.org/10.1016/j.paerosci.2018.03.006 and arxiv.org/abs/2608.15087\n"
        "Evidence openalex_W3164623820; mirror https://annas-archive.pk/md5/abc\n"
        "Site https://www.esa.int/HAPS"
    )
    leads = {(kind, ident) for kind, ident, _, _ in extract_leads(text)}
    assert ("doi", "10.1016/j.paerosci.2018.03.006") in leads
    assert ("arxiv", "2608.15087") in leads
    assert ("openalex", "W3164623820") in leads
    assert ("url", "https://www.esa.int/HAPS") in leads
    assert not any("annas-archive" in ident for _, ident in leads)


def test_duplicates_by_hash_and_doi():
    def row(fid, sha, doi="", size=1):
        return IndexRow(fid, f"PDFs/{fid}.pdf", "paper", "TBD", "pdf", size, sha, doi=doi)

    rows = [row("P001", "aa", size=5), row("P002", "aa"), row("P003", "bb", "10.1/x"),
            row("P004", "cc", "10.1/x", size=9), row("P005", "dd")]
    groups = find_duplicates(rows)
    assert {g["file_ids"] for g in groups} == {"P001 P002", "P003 P004"}
    assert rows[1].duplicate_of == "P001" and rows[2].duplicate_of == "P004"
    assert rows[4].duplicate_of == ""


def test_iter_files_skips_generated_and_lock_files(tmp_path):
    from haps.io.literature import iter_files

    for rel in ["papers/a.pdf", "text_copies/reviews/r.md", "papers/_duplicates/b.pdf",
                "~$lock.docx", "ai_derived/reviews/x.docx"]:
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("x")
    found = {p.relative_to(tmp_path).as_posix() for p in iter_files(tmp_path)}
    assert found == {"papers/a.pdf", "ai_derived/reviews/x.docx"}
