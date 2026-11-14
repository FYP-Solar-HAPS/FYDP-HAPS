# literature/ — reading rules for people and agents

These rules apply to every team member and every AI agent. `AGENTS.md` links here.
They put PLAN.md §3.8 (literature ingestion and the evidence register) into practice.

## 1. Where things are

There are two places. The **shared drive** holds the original files. The **repository** holds small
text files that describe, index and check them. Nothing in this folder modifies the drive.

### 1.1 Shared drive: `fydp-haps-data/literature/` (originals, never in Git)

```
literature/
├── papers/                    the papers, reports, theses and books (PDF)   tier A or B, decided per file
├── ai_derived/                everything an AI tool produced                tier C, never cited
│   ├── reviews/               written literature reviews (Jenni AI, Paperguide, chatbot index)
│   ├── watch_reports/         Scientific Watch Report PDFs (trends, gaps, synthesis)
│   ├── source_lists/          lists of sources (Consensus, Jenni, Paperguide, CSV exports)
│   └── extraction_tables/     per-paper data an AI extracted (Paperguide table)
├── team_lists/                link lists the team compiled by hand
├── text_copies/               plain-text copies of ai_derived/ and team_lists/ (made by `copies`)
└── _not_for_repo/             material that must never enter the repository (see §6)
```

`text_copies/` lives on the drive, not in Git, because the repository is public and these copies
contain publisher abstracts. Everyone reads them there; agents get the drive path from `LOCATION.md`.

### 1.2 Repository: `literature/` (this folder)

| File or folder | What it is | Made by |
|---|---|---|
| `README.md` | These rules | Team |
| `SOURCES_INDEX.md` | One entry per non-paper file: what it is, how to read it, known defects | Team (update when a file is added) |
| `LOCATION.md` | Link to the shared-drive folder | Team |
| `index.csv` | One row per drive file: ID, path, category, tier, SHA-256, title, DOI, citekey, status | `index` command, then completed by T-LIT.01 |
| `duplicates.csv` | Files that are the same work (same hash, DOI, arXiv ID or title) | `index` command; `decision` column filled by a person |
| `library.bib` | BibTeX for every paper, exported from Mendeley | Mendeley export (never edit by hand) |
| `ai_leads.csv` | Every DOI, URL, arXiv ID and OpenAlex ID the AI files mention, with a check status | `leads` command, then T-LIT.01 |
| `gap_register.csv` | Every research gap an AI file claims, with a verification status | `gaps` command plus manual rows, then T-LIT.03 |
| `evidence_register.csv` | Claims, values and equations used by the models, each traced to a page | T-LIT.02 onward (PLAN.md §3.8 step 3) |
| `notes/` | Human-checked notes on individual papers, one file per citekey | Team, as needed |

## 2. Trust tiers (from PLAN.md §3.8)

| Tier | Meaning | May be cited? |
|---|---|---|
| **A** | Peer-reviewed journal or conference paper, thesis, NASA/ESA/agency report, textbook | Yes, with page, figure, table or equation number |
| **B** | Preprint (arXiv, TechRxiv, Preprints.org), manufacturer datasheet, official programme release, patent | Yes, labelled as such; prefer an A source when one exists |
| **C** | Anything written by an AI tool: reviews, summaries, "takeaways", gap lists, extraction tables, chatbot answers | **Never** |
| list | A team link list. Each linked item gets its own tier when it is indexed | The list itself: never |

A paper's tier is set in `index.csv` during T-LIT.01. A PDF being in `papers/` does not make it tier A.
Websites (Wikipedia, news, blogs, company pages) are not tier A or B. Use them only to find a
primary source. An official programme page may count as B if no paper exists.

## 3. Binding rules

1. **Cite only papers.** Every citation in a report, card, `criteria.yaml` or code comment points to a
   citekey in `library.bib` and a location (page, figure, table or equation). It never points to a
   file in `ai_derived/` or `text_copies/`.
2. **AI files are leads, not evidence.** Use them to find papers and questions. Before a claim from an
   AI file is used anywhere, open the paper it refers to, find the statement, and record it in
   `evidence_register.csv` with the page number. If the paper does not say it, the claim is dropped.
3. **Numbers need a page.** No number (efficiency, mass fraction, specific energy, wing loading,
   percentage gain, cost) from an AI file enters a model, `criteria.yaml` or a report until it is
   traced to a page of a tier A or B source.
4. **No AI text in reports.** Do not copy or lightly reword sentences from AI-derived files into any
   report, slide or paper. Write from the primary sources. Text produced by an AI tool and submitted
   under the team's names is still AI text, whoever's name is on the file.
5. **Check that a source exists before using it.** Every source an AI file names gets a row in
   `ai_leads.csv` (identifiers) or is found during T-LIT.01 (titles). Mark `exists` = `YES` only
   after resolving it (§5). AI tools invent references and get details wrong; a reference that
   cannot be found is marked `NO` and never used.
6. **A gap is real only when it has been searched for.** A gap from an AI file stays `UNVERIFIED`
   until someone has (a) read the papers it rests on and (b) run and recorded a search showing no
   paper already fills it (§7).
7. **Never edit drive originals.** Work from the text copies. If an original changes, rerun the
   commands (§4) so hashes and copies stay current.
8. **One copy per work.** When `duplicates.csv` lists a group, one person decides which file to keep
   (`decision` column). The others move to `papers/_duplicates/` on the drive. They are never deleted
   until the gate G0 review.
9. **Agents report, people verify.** An agent may fill any column. Only a team member may set
   `exists`, `status` or `tier` as final (initials and date in `checked_by` and `date`).

## 4. Commands

Run from the repository root with the `haps` environment active. Replace `<drive>` with the local path
of the shared drive (for example `G:\My Drive\fydp-haps-data`). The commands only read the drive.

```
python -m haps.io.literature index  --src "<drive>/literature" --out literature
python -m haps.io.literature copies --src "<drive>/literature" --out "<drive>/literature/text_copies"
python -m haps.io.literature leads  --src "<drive>/literature" --out literature/ai_leads.csv --index literature/index.csv
python -m haps.io.literature gaps   --src "<drive>/literature" --out literature/gap_register.csv
```

- `index` takes a few minutes for about 200 PDFs (it hashes every file and reads the first two pages).
**Intake order (card T-LIT.00, once).** The repository already contains `ai_leads.csv` and
`gap_register.csv`, generated on 15 Nov 2026 from the 22 non-paper files laid out as in §1.1.
After reorganising the drive to §1.1:
1. Run `index` (creates `index.csv` and `duplicates.csv`).
2. Run `leads` with `--index literature/index.csv --force` so leads already in the library are marked.
3. Run `copies` to write `text_copies/` on the drive. Rerun it whenever a drive file changes.
4. Decide every group in `duplicates.csv`, then export `library.bib` from Mendeley (§8).
5. Commit everything on a branch `card/T-LIT.00-literature-intake` and open a pull request.

- `index`, `leads` and `gaps` refuse to overwrite an existing CSV, because people fill in columns
  of these files. `--force` overwrites and loses those edits. To add new drive files later, write to
  a new name (for example `--out literature/new`) and merge the new rows by hand.
  `copies` always overwrites: text copies are regenerated, never edited.
- The tools recognise both the layout in §1.1 and the original folder names
  (`PDFs`, `Literature Review`, `Scientific Watch Report`, `Sources in ... files`).
- They need `pymupdf` and `python-docx`: `pip install -e ".[literature]"` (T-W0.02 adds both to
  `env/environment.yml`).

## 5. How to read each kind of file

### 5.1 By format

| Format | How to read it | Watch for |
|---|---|---|
| PDF, paper | PyMuPDF: `pymupdf.open(p)`, then `page.get_text()`; for layout or tables, `page.get_text("blocks")` | `index.csv` notes "probably scanned, needs OCR" when there is no text layer. Equations often extract badly: read them from the rendered page. |
| PDF, AI report | Read the text copy in the drive's `text_copies/` | Tables flatten into lines |
| `.docx` | Read the text copy (made with python-docx, keeping in-text citations) | Headings marked `##`; tables become Markdown tables |
| `.txt` | Plain UTF-8 text | Entries separated by blank lines; layout differs by tool (see `SOURCES_INDEX.md`) |
| `.md` | Markdown | Escaped characters (`\_`) inside URLs |
| `.csv` | `pandas.read_csv(p, encoding="utf-8-sig")` | Columns differ by tool (see `SOURCES_INDEX.md`); author lists separated by `\|` in some exports |
| `.bib` | `bibtexparser` (v2) or read as text | Mendeley citekeys can collide (`Noth2008`, `Noth2008a`) |

### 5.2 By kind

| Kind | Use it for | Do not use it for |
|---|---|---|
| Review (`ai_derived/reviews/`) | Seeing how the field is usually organised; finding which papers to read for a topic | Facts, numbers, quotes or wording in any team document |
| Watch report (`ai_derived/watch_reports/`) | Candidate trends and gaps; OpenAlex IDs of papers to read | Gap or trend claims as findings; "maturity" labels |
| Source list (`ai_derived/source_lists/`) | Finding candidate papers; titles, DOIs and venues to check | "Takeaway", abstract summaries or study-type labels as evidence |
| Extraction table (`ai_derived/extraction_tables/`) | Knowing where in a paper to look | Any extracted value, until checked against the paper |
| Team list (`team_lists/`) | Finding sources | Citing web pages as tier A |

## 6. What never goes into the repository

- PDFs, `.docx` originals and other drive files (`.gitignore` blocks them under `literature/`).
- Text copies of literature files (`text_copies/`): the repository is public and they contain
  publisher abstracts and AI-written text. `.gitignore` blocks `literature/text_copies/`.
- Links to shadow libraries (Anna's Archive, Library Genesis, Sci-Hub, Z-Library). The `copies`
  command replaces them with `[link removed: shadow library]` and `leads` skips them.
  `_not_for_repo/` holds such files on the drive only.
- Account links or shared-chat links that give access to someone's AI-tool account.

Cite the published version of a work (publisher, DOI, ISBN), never the place it was downloaded from.

## 7. Columns that need people

### 7.1 `ai_leads.csv`

| Column | Values |
|---|---|
| `in_library` | `file_id` from `index.csv` if the work is already in `papers/` (filled automatically for DOI and arXiv leads when `--index` is given) |
| `exists` | `YES` (resolved and the metadata match the AI file), `WRONG_DETAILS` (exists but title, authors, year or venue differ; say what in `notes`), `NO` (cannot be found), `NOT_CHECKED` |
| `checked_by`, `date` | Initials (SU, AR, HA) and ISO date |

How to resolve: DOI → open `https://doi.org/<doi>` or query `https://api.crossref.org/works/<doi>`.
arXiv → `https://arxiv.org/abs/<id>`. OpenAlex → `https://openalex.org/<id>` or
`https://api.openalex.org/works/<id>`. A URL → open it and record the work it points to.
Only leads that matter to a module, a requirement or a gap need checking; mark the rest `NOT_CHECKED`.

### 7.2 `gap_register.csv`

| Column | Values |
|---|---|
| `status` | `UNVERIFIED` (default), `CONFIRMED`, `PARTLY`, `REJECTED` (a paper already fills it), `NOT_RELEVANT` (outside this project's scope) |
| `supporting_papers` | Citekeys with pages that show the gap exists |
| `contradicting_papers` | Citekeys of papers that already fill it |
| `relevance_to_project` | Which requirement, module or claim of this project it bears on, or "none" |
| `notes` | For `CONFIRMED`: database(s) searched (Scopus, Web of Science, Google Scholar, IEEE Xplore, AIAA ARC), search string, date and number of hits screened |

`CONFIRMED` needs both supporting papers and a recorded search. Gaps found while reading papers or
the JenniAI and Paperguide reviews are added by hand with the next free `gap_id`.

### 7.3 `index.csv` (completed in T-LIT.01)

`title`, `authors`, `year`, `venue`, `doi` (where the first pages had none), `type` (journal,
conference, thesis, report, preprint, book, patent, web), `tier`, `topic_tags` (PLAN.md §7 module
names: atmosphere, solar, pv, aero, propulsion, mass, structures, energy, stability, cost, comms,
regulation), `citekey` (from `library.bib`), `status` (`AUTO` → `CHECKED`).

## 8. Mendeley and `library.bib`

1. In Mendeley Reference Manager, add every PDF in `papers/` to one collection named `fydp-haps`.
2. Check the metadata Mendeley found (title, authors, year, venue, DOI) against each PDF's first page.
   Fix it in Mendeley, not in the `.bib` file.
3. Select all references in the collection and export them as BibTeX to `literature/library.bib`.
4. Re-export after every change. The `.bib` file is generated; it is never edited by hand.
5. T-LIT.01 copies each paper's citekey into `index.csv`, matching on DOI, then title.
