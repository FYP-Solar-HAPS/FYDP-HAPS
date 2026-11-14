# SOURCES_INDEX — what each non-paper file is and how to read it

One entry per file in `ai_derived/`, `team_lists/` and `_not_for_repo/` on the shared drive.
Papers are catalogued in `index.csv`, not here. Read `README.md` first: every file below is
**tier C or a link list, and is never cited.**

Audit of the drive folder on 15 Nov 2026 (before reorganisation): 217 items = 194 PDFs in `PDFs/`,
22 AI-derived or list files (including the ResearchRabbit CSV added that day), and 1 Word lock file (see §6). "File date" is the last-modified date
on the drive, not necessarily the date the tool produced the content.

Each text copy is on the drive in `literature/text_copies/<subfolder>/<lower_case_name>.md` (or `.csv`), made by the `copies` command (README §4).

---

## 1. `ai_derived/reviews/` — written literature reviews

### 1.1 `Solar HAPS_HALE literature review JenniAI.docx`
- **Tool:** Jenni AI. **File date:** 27 Oct 2026. **Size:** ≈41,000 words.
- **Title in file:** "Solar-Powered High-Altitude Platforms, Long-Endurance Drones, and Pseudo-Satellites: A Literature Review".
- **Structure:** themed sections (terminology, history, platform classes, applications, energy,
  aerodynamics and structures, communications, regulation), a "Gaps in the Literature" section, and
  author–year in-text citations.
- **How to read:** text copy. Citations appear as `(Author et al., year)`; match them to `library.bib` by author and year, then confirm the title.
- **Known issues:** see §1.2 for the near-duplicate versions.

### 1.2 `Solar HAPS_HALE literature review JenniAI - same.docx`
- **Tool:** Jenni AI. **File date:** 27 Oct 2026. **Size:** ≈41,000 words.
- **Relation to 1.1:** about 94 % of the text is identical (automatic comparison). It is a second
  version of the same review, with a table of contents.
- **Known issue:** the title page carries "Ateeq-ur-Rehman, October 2026" as the author line. The
  text was written by Jenni AI. It must never be submitted, or quoted, as team writing (README §3 rule 4).
- **Team decision (15 Nov 2026):** all three JenniAI files (1.1, 1.2, 1.3) are kept and read. 1.1 and
  1.2 differ mainly in formatting, styling and layout; 1.3 is the chat answer from the same session.
  Where they disagree on a fact, none of them wins: the cited paper decides.

### 1.3 `Solar HAPS_HALE literature review JenniAI - chat response.docx`
- **Tool:** Jenni AI (chat answer saved to Word). **File date:** 27 Oct 2026. **Size:** ≈7,000 words.
- **Title in file:** "High-Altitude Solar Platforms, Long-Endurance Aircraft, and Pseudo-Satellites: A Comprehensive Literature Review".
- **Structure:** 22 numbered sections; section 22 is "Research Gaps and Future Directions".
- **Relation:** the same text as `Ai_Jenni_1.txt` (§1.5).

### 1.4 `Chat _ Paperguide.pdf`
- **Tool:** Paperguide (chat page printed to PDF on 17 Oct 2026). **Pages:** 12.
- **Structure:** abstract, introduction, themed sections, reference list with DOIs.
- **How to read:** text copy. The reference list's DOIs are in `ai_leads.csv`.
- **Known issues:** the abstract states several quantitative results (percent gains, energy totals,
  endurance hours, payload scaling). None may be used until traced to the cited paper and page.

### 1.5 `Ai_Jenni_1.txt`
- **Tool:** Jenni AI. **File date:** 17 Oct 2026.
- **Content:** the same review as §1.3, preceded by a note from the tool saying it corrected a
  citation that had merged two different claims. Treat it as the text form of §1.3.

### 1.6 `new proposal literature.txt`
- **Tool:** an AI tool (name not recorded; supplied by a team member). **File date:** 5 Aug 2026.
- **Content:** "Literature Index: AEGIS-HAPS Verification & Validation": papers grouped by category,
  each with "relevance" and "benchmark parameters", and advice on answering evaluators.
- **Known issues:** it states quantitative claims with no source (for example an energy-degradation
  percentage range that "standard" models miss). Report numbers and identifiers in it are unchecked.
  Use it only as a list of papers to look up.

---

## 2. `ai_derived/watch_reports/` — Scientific Watch Report PDFs

All four are produced by the "Scientific Watch Report agents (ReAct+Reflexion)" tool. Each has:
a cover table (topic, articles fetched and selected, tokens used), **1. Trends, Gaps & Future
Perspectives** (trend table with a maturity label, research gaps marked `[HIGH]` or `[MEDIUM]` with
suggested actions, future perspectives), **2. Global Synthesis** (overview, approaches, key findings)
and per-article summaries. Evidence is given as OpenAlex work IDs (`openalex_W…`), which resolve at
`https://openalex.org/W…`.

| File | Topic | Generated | Articles fetched → selected | Full text read |
|---|---|---|---|---|
| `high_altitude_platform.pdf` | high altitude platform | 19 Oct 2026 | 114 → 15 | 8 of 15 (rest from abstracts) |
| `solar_powered_high_altitude_uav.pdf` | solar powered high altitude uav | 19 Oct 2026 | 120 → 15 | 3 of 15 (rest from abstracts) |
| `solar_powered_high_altitude_long_endurance_platforms.pdf` | Solar-powered HALE platforms | 4 Oct 2026 | 39 → 10 | not stated |
| `solar_powered_high_altitude_pseudo_satellite_platforms.pdf` | Solar-powered HAPS platforms | 4 Oct 2026 | 40 → 10 | not stated |

- **How to read:** text copies; gaps are already in `gap_register.csv` (G001–G013).
- **Known issues:**
  - Each report rests on 10–15 papers, mostly read from abstracts only. A gap claimed from that
    is a hypothesis, not a finding.
  - Some trends and gaps are off-topic or doubtful for solar HALE aircraft (for example precision
    agriculture labelled an "established" application, and a gap about "RAID technologies").
  - Maturity labels (`EMERGING`, `ESTABLISHED`) and priorities (`HIGH`, `MEDIUM`) are the tool's
    opinion and carry no weight.

---

## 3. `ai_derived/source_lists/` — lists of sources

| File | Tool | File date | Entries | Layout of one entry |
|---|---|---|---|---|
| `high altitude (solar) platforms_drones, … - 17 Oct 2026.csv` | Consensus | 17 Oct 2026 | 20 rows | Columns: Title, Takeaway, Authors, Year, Citations, Abstract, Study Type, Journal, Journal SJR Quartile, DOI, Consensus Link |
| `literature_researchrabbit.csv` | ResearchRabbit | 15 Nov 2026 | 143 rows | Columns: DOI, Title, Authors, Journal, Year, Abstract, ResearchRabbitId, Cited By, References, PubMedId |
| `works-csv-LxYuHMiYwQqdAYyAQf2fHC.csv` | AI search tool, name not recorded (see note) | 17 Oct 2026 | 3,309 rows | Columns: Title, Author, Year, Citation count, Open access |
| `works-csv-bTq4wHrWor8XtiaZPK6ed4.csv` | AI search tool, name not recorded | 5 Oct 2026 | 121 rows | Columns: Title, Author, Year, Citation count, Open access, Source, Abstract |
| `works-csv-nFeSLRk7wBppCAkzeUKePg.csv` | AI search tool, name not recorded | 5 Oct 2026 | 180 rows | Same as above |
| `Ai_Consensus_1.txt` | Consensus | 17 Oct 2026 | ≈10 results + AI summary | Title / authors • year / snippet; then a summary with Markdown links |
| `Ai_Consensus_2.txt` | Consensus | 17 Oct 2026 | ≈250 | Title / year / authors / venue, entries separated by blank lines |
| `Ai_Jenni_2.txt` | Jenni AI | 17 Oct 2026 | ≈300 | Title / authors / venue / `·` / year |
| `Ai_Paperguide_1.txt` | Paperguide | 17 Oct 2026 | ≈100 | Title / year / authors / abstract / venue |

Notes:
- **Only one CSV comes from Consensus.** The three `works-csv-…` files were exported by a team member
  from an AI search tool (keyword in, CSV out; tool name not recorded). They have no DOI column, so
  they must be matched by title. If the tool is identified later, record it here.
- **ResearchRabbit CSV:** ResearchRabbit builds lists from citation links, and its columns come from
  bibliographic databases rather than generated text, so its metadata is more reliable than the other
  lists. It is still a list (never cited). 117 of 143 rows have a DOI; 26 say `(missing DOI)` and
  must be matched by title. `Cited By` and `References` are counts within ResearchRabbit's
  database, not citation counts to quote.
- `works-csv-LxYu…` (3,309 rows) is a broad search export, not a curated list. Its first rows are on
  optical (FSO) networking and its sister file `nFeS…` starts with lithium–sulfur batteries. Filter by
  topic before reading; do not treat it as "the literature".
- The Consensus "Takeaway", "Study Type" and "Journal SJR Quartile" columns are generated or looked
  up by the tool. Check the quartile in SCImago (https://www.scimagojr.com) before quoting it.
- **Known defect, `Ai_Consensus_1.txt`:** papers with arXiv numbers `2608.xxxxx` show "2608" where
  the year should be; the tool read the arXiv number as a year. Check every year and venue.

---

## 4. `ai_derived/extraction_tables/`

### 4.1 `Ai_Paperguide_2.txt`
- **Tool:** Paperguide. **File date:** 17 Oct 2026. **Entries:** 20 numbered papers.
- **Layout of one entry:** number / title / venue / year / authors, then unlabelled paragraphs in a
  fixed order: platform type, method or concept, altitude regime, energy approach, propulsion, communications, evaluation method, key results.
- **How to read:** use it to find where to look in each paper. Every value is unverified until read
  in the paper and entered in `evidence_register.csv` with a page number.

---

## 5. `team_lists/`

### 5.1 `HAPS  HALE LITERATURE.md`
- **Compiled by:** a team member, by hand. **File date:** 20 Sep 2026.
- **Content:** 141 numbered URLs: ESA pages, NASA ADS abstract pages, ScienceDirect, GSMA and
  Frontex reports, academia.edu, Wikipedia, a geography website, and three shadow-library search links
  (removed in the text copy).
- **How to read:** each URL is in `ai_leads.csv` (`kind` = `url`). Open the ones relevant to a module
  and index the underlying paper or report. Wikipedia and general websites are never cited.

---

## 6. `_not_for_repo/` and clean-up

### 6.1 `Annas sources.txt`
- **Content:** 68 unique download links to a shadow library (Anna's Archive), with no titles. File date 5 Oct 2026.
- **Compiled by:** a team member, by hand.
- **Rule:** stays on the drive in `_not_for_repo/`. It is not copied, indexed for leads or committed.
- **Action:** each work used is entered in Mendeley with its published reference (title, authors,
  publisher, year, DOI or ISBN) and cited by that, never by the link.

### 6.2 Word lock file in the root of `Literature/`
- `~$lar_powered_high_altitude_platforms__long_endurance_drones__and_pseudo_satellites__a_literature_review.docx`
  (162 bytes) is a temporary file Word leaves while a document is open, here for the JenniAI review in
  §1.1 under its earlier name. It is not literature. Delete it when Word is closed. It is why the folder
  shows 216 items instead of 215.

---

## 7. Duplicates among the 194 PDFs (to confirm with `duplicates.csv`)

Confirmed on 15 Nov 2026 by opening both files:
- `electronics_09_00179_v2.pdf` (University of York repository copy) and
  `electronics-09-00179-with-cover.pdf` (publisher copy): same paper, DOI 10.3390/electronics9010179.

Likely, from file names and identical sizes (the `index` command will confirm by hash, DOI or title):
- `System_Design_of_Gigabit_HAPS_Mobile_Communication.pdf` and `…Communications.pdf` (same size, 2,255,788 bytes).
- `744005fa59312b4723b522de46fcc63aebaf.pdf`, `Design_of_Energy-Management_Strategy_for_Solar-Pow.pdf`
  and `sustainability-15-14972.pdf` (all 5,565,511 bytes), and possibly `sustainability-15-14972-with-cover.pdf`.
- `A Vision and Framework for the High Altitude Platform Station (HAPS) Networks of the Future.pdf` and `A_Vision_and_Framework_for_the_High_Alti.pdf`.
- `Gradient-Based Optimization of Solar-Regenerative High-Altitude L.pdf` and `… L (1).pdf`.
- `Multidisciplinary Design Optimization of Flexible Solar-Regenerat.pdf` and `multidisciplinary-design-optimization-of-flexible-solar-17u1pyhubv.pdf`.

The number of distinct works is therefore below 194; `index.csv` gives the exact count.
