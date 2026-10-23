# UUCMS Playwright Login

A separate Python/Playwright login automation project. It coexists with
the existing Java/Selenium/TestNG UUCMS framework.

## Setup

``` powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -e .
py -m playwright install chromium
Copy-Item .env.example .env
Copy-Item test_data\login\LoginData.example.json test_data\login\LoginData.json
```

Set usernames in the Excel workbook or JSON registry described below, then
define the password environment variable in your local `.env`. The `captcha`
field defaults to `12345`. Keep the URL, browser, headless mode, and timeout
in `.env`. Set `UUCMS_BROWSER` to `chromium`,
`firefox`, or `webkit`; the test, Codegen, video recorder, and one-click
runner all use that value. The example uses `http://123.63.4.210:5010/`.
Login data is ignored by Git.

## Role-based authentication

Store accounts in either `test_data/login/LoginData.xlsx` or
`test_data/login/LoginData.json`. If the Excel workbook exists, it is used
instead of JSON; otherwise the loader falls back to JSON. Do not leave an
invalid or incomplete workbook in place expecting JSON fallback.

The workbook must have a `Roles` worksheet (or use its first worksheet) with
these columns:

| role_key | username | password_env |
|---|---|---|
| default | default account username | UUCMS_TEST_PASSWORD |
| candidate_1 | first candidate username | UUCMS_TEST_PASSWORD |
| candidate_2 | second candidate username | UUCMS_TEST_PASSWORD |

Use a unique `role_key` per account and include exactly one `default` row.
Store usernames as text in Excel to preserve leading zeros.
`password_env` is optional; if omitted, the account uses
`UUCMS_TEST_PASSWORD`. For JSON, store the default account at the top level
and the other accounts in the `roles` object. Role keys can be
`student`, `deputy_registrar`, `registrar_evaluation`, and
`university_admin_university_1`. The default account uses top-level
`username` and `password_env`; each role entry uses the same fields.

Define the password environment variable(s) in your local `.env`, not in the
workbook or JSON. For example, if all accounts share one test password, set
`UUCMS_TEST_PASSWORD=...` once and use that name for every account. Only add
roles needed by your tests, and never commit real credentials.

Use distinct keys for accounts belonging to different universities, such as
`university_admin_university_1` and `university_admin_university_2`.

Ph.D actors move through three phases: **Candidate** before admission
(its own login number), **Student** after admission, and **Scholar**
after the synopsis is approved and the permanent USN is generated. The
Student and Scholar phases use the same USN for login; the Candidate
phase uses a different number. Pick the role key that matches the phase
of each stage (`candidate`, `student`, `scholar`).

All tests use the same `login_as` fixture to sign in or switch accounts:

```python
def test_registrar_approves(page, login_as):
    login_as("registrar_evaluation")
    # Continue using the authenticated page.
```

Use `authenticated_page` when a test only needs the configured default
account. Both fixtures share the central `RoleManager`; role-specific
test suites do not need separate login helpers.

## Project structure

```text
config/                          Runtime settings and environment configuration
src/uucms/
├── auth/                        Login page and authentication behaviour
├── core/                        Shared Playwright page abstractions
├── constants/                   Roles, statuses, menus, and menu paths
├── modules/
│   ├── admission/
│   │   └── pages/               Application, payment, registration, approvals
│   ├── academics/pages/
│   ├── exam/pages/
│   ├── research_development/
│   │   └── pages/
│   └── common/                  Shared dashboard and menu page objects
├── workflows/                   Cross-module workflows
│   ├── phd_workflow.py
│   └── research_development/
└── fixtures/
tests/
├── unit/
└── ui/
    ├── admission/
    ├── authentication/
    ├── exam/
    └── research_development/
test_data/                        JSON test data and example templates
utils/                            JSON, logging, screenshot, and wait helpers
```

## Codegen to POM workflow

1.  Start with a normal login recording:

    ``` powershell
    .\record_login.bat
    ```

2.  Perform the login flow in the opened browser. Do not type real
    credentials if the generated recording will be shared; codegen can
    capture typed values.

3.  Review the generated file under `recordings/`. Raw Python recordings
    are temporary and ignored by Git.

4.  Paste the recording into `prompts/antigravity-pom-conversion.md` and
    use the documented Gemini-in-Antigravity prompt.

5.  Review the returned selectors and waits, then apply only the
    maintained POM changes under `src/uucms/modules` and `tests`.

6.  Run the maintained test with the one-click script:

    ``` powershell
    .\run_login.bat
    .\scripts\run-login.ps1
    .\scripts\run-login.ps1 -Headed
    ```

The one-click runner installs Chromium when needed and executes the
maintained test. It does not record a new flow or invoke AI conversion.
Antigravity and Gemini are authoring tools only; the finished test runs
locally.

## Exam module

Create the Exam test-data file from its template:

``` powershell
Copy-Item test_data\createNotificationData.example.json test_data\createNotificationData.json
```

After recording the Exam workflow, enter every field selector and value,
submit selector, and success selector in
`test_data/createNotificationData.json`. Use `select_label` with one
visible dropdown label, such as `2025-2026` or `regular`. Use
`multiselect_labels` with comma-separated visible labels for custom
multiselects, for example `Program One, Program Two`; use `fill` for
text/date fields and `upload` for files. The test logs in using
`loginData.json`, opens the Exam module, fills all configured fields,
submits the form, and checks the configured success element. The raw
Codegen file is removed after conversion because it can contain typed
credentials; the video recording remains under `recordings/videos/`.

Run only the Exam test:

``` powershell
.venv\Scripts\python.exe -m pytest tests\ui\exam\test_exam.py -m exam -v
```

The Exam test intentionally stops with a clear error while
`examData.json` still contains `REPLACE_WITH` placeholders. This
prevents guessed selectors from creating unreliable automation.

## Admission module

The admission module automates the full Ph.D admission lifecycle:
candidate application (program selection, previous-education
declaration, details, offline payment), chairperson entrance view /
cut-off marks / review & approve / entrance marks, Registrar (Admin)
approvals, interview invites and interview marks, student invites,
admission document verification with the Ph.D mapping (discipline,
area of research, guide, category, quota, research student type), and
the final offline payment.

Create the admission test-data file from its template:

``` powershell
Copy-Item test_data\admission\phd_admission.example.json test_data\admission\phd_admission.json
```

After recording each screen, fill every `REPLACE_WITH_*` selector and
value in `test_data/admission/phd_admission.json`. Each stage carries a
`login` role key, and multi-role stages switch accounts through the
`login_as` fixture. Run only the admission tests:

``` powershell
.venv\Scripts\python.exe -m pytest tests\ui\admission\test_admission.py -m admission -v
```

The admission tests intentionally stop with a clear error while their
test-data file still contains `REPLACE_WITH` placeholders.

## Academics (coursework) module

The coursework module automates chairperson application review, student
course registration, Registrar (Evaluation) course modification, internal
assessment marks, and attendance. Those stages are orchestrated by the
coursework workflow; separate exam screens are under
`src/uucms/modules/exam/pages`.

Create the coursework test-data file from its template:

``` powershell
Copy-Item test_data\academics\coursework_examination.example.json test_data\academics\coursework_examination.json
```

After recording each screen, fill every `REPLACE_WITH_*` selector and
value in `test_data/academics/coursework_examination.json`. Coursework
stages use the `login` role key and shared `login_as` fixture. Run only
the coursework tests:

``` powershell
.venv\Scripts\python.exe -m pytest tests\ui\academics\test_coursework.py -m academics -v
```

The coursework tests intentionally stop with a clear error while their
test-data file still contains `REPLACE_WITH` placeholders.

The Exam workflow provides dedicated page objects and tests for
permitting students, exam-center approval, QP-code updates, evaluation
marks entry, and hall-ticket eligibility. The first four screens always
authenticate as `registrar_evaluation`; hall tickets authenticate as
`principal`, using the shared role registry and `login_as` fixture.
These exam screens currently use the corresponding stage data in
`test_data/academics/coursework_examination.json`. Run them with:

``` powershell
.\run_exam.bat
```

## Academics (program setup) module

The program setup module automates the Ph.D program and curriculum setup
across admin roles: State Admin creates the statewise program details
and the first discipline/subject combination; University Admin maps the
program (new program data, disciplines, Areas of Research, evaluation
system), creates the scheme, maps programs and course types, designs the
courses with credit and evaluation components, configures term and
course-type credit details (freeze + validate), and builds the CBCS
curriculum; College Admin selects the electives. The screen page
objects live under `src/uucms/modules/academics/pages/` and the
workflow under `src/uucms/workflows/program_setup_workflow.py`.

Create the program setup test-data file from its template:

``` powershell
Copy-Item test_data\academics\program_setup.example.json test_data\academics\program_setup.json
```

After recording each screen, fill every `REPLACE_WITH_*` selector and
value in `test_data/academics/program_setup.json`. Stages run as the
`state_admin`, `university_admin`, and `college_admin` roles from
`test_data/login/LoginData.json`, switching accounts through the shared
`login_as` fixture. Run only the program setup tests:

``` powershell
.venv\Scripts\python.exe -m pytest tests\ui\academics\test_program_setup.py -m academics -v
```

The program setup tests intentionally stop with a clear error while
their test-data file still contains `REPLACE_WITH` placeholders.

## Video recording

To save a video of the browser session while you work through a
workflow:

``` powershell
.\record_video.bat
```

To start on a specific page instead of the configured base URL, pass
the page URL:

``` powershell
.\record_video.bat --url <page-url>
```

Complete the flow in the opened browser, then return to the terminal and
press Enter. The `.webm` video is saved under `recordings/videos/`.
Videos can contain credentials or other sensitive page data, so review
them before sharing.

## Codegen recording (GUI)

To record a workflow with the Playwright codegen browser, with the live
generated Python code printed in the console:

``` powershell
.\record_codegen.bat
```

Click **Start Codegen**, do the workflow in the codegen browser window,
then click **Stop Codegen** (or close that browser window). The generated
file is saved under `recordings/` as `workflow_<timestamp>_codegen.py`
and is the input for `prompts/<module>-pom-conversion.md` when writing
the page objects and tests.

## CAPTCHA

This project accepts a configured CAPTCHA value through `UUCMS_CAPTCHA`,
currently defaulted to `12345`. It does not attempt to solve or bypass
visual CAPTCHA challenges. A test environment with a supported
automation policy is required for unattended runs. If CAPTCHA is entered
manually during recording, remove that value from the generated script
before keeping it.

## Validation

The login test asserts that `#MenuDiv` is visible after submission.
Failures retain Playwright traces and screenshots under `test-results/`
without intentionally logging secret values.

## Research & Development (R&D) module

The R&D workflow is added as a separate functional area on top of the
existing Login and Exam automation. It covers the Ph.D lifecycle from
admission/coursework through research progress, final thesis/symposium,
convocation eligibility, and university research projects.

### R&D workflow overview

``` text
Ph.D Admission
    ↓
Guide / Area of Research / Provisional USN
    ↓
Course Work
    ↓
R&D Phase 2 – Synopsis
    ↓
Synopsis Approval
    ↓
Permanent USN / Ph.D Scholar
    ↓
R&D Phase 4 – Progress Reports
    ↓
Final Progress Report / Thesis
    ↓
Final Viva Voce / Colloquium / Symposium
    ↓
Registrar (Evaluation) Approval
    ↓
Ph.D Convocation Eligibility
```

### 1. Admission and R&D prerequisites

**State Admin** - Creates the Doctor of Philosophy programme under the
Ph.D programme level. - Configures prerequisites and minimum programme
duration. - Maps disciplines and department discipline codes to the Ph.D
programme.

**University Admin** - Maps the Ph.D programme and configures maximum
duration, including applicable extensions and leave. - Configures
minimum eligibility criteria using percentage/CGPA, gender and
category. - Configures accepted external-exam exemptions such as UGC
NET, CSIR and GATE. - Configures designation-wise maximum guide limits
by academic year/category. - Configures Ph.D/R&D payment accounts and
PayGov service details. - Maps disciplines to departments and
departments to Department Chairpersons. - Creates Areas of Research and
maps them to disciplines. - Maps faculties to Areas of Research.

**Department Chairperson** - Configures minimum entrance-exam and
interview marks. - Enters entrance-exam marks and sends them to
Registrar (Admin) for approval. - Schedules student interviews and
enters interview marks. - Creates category-wise guide seat/vacancy
matrix and sends it for approval. - Creates/maps Areas of Research and
guide allocations. - Performs guide allocation based on approved vacancy
matrix and student category. - Enters the student's Area of Research and
supports provisional USN generation.

**Registrar (Admin)** - Approves/rejects entrance-exam marks, interview
marks and guide vacancy/seat matrix.

**Student/Candidate** - Applies for Ph.D admission. - Enters PG marks
and external-exam details. - Uploads supporting documents. - Completes
the applicable admission payment after eligibility/admission processing.

### 2. Academics and Examination integration

-   University Admin configures Ph.D coursework curriculum
    discipline-wise and programme-wise with credits and course details.
-   Research-area-related courses can be configured as electives for
    students under the relevant discipline.
-   IA/attendance or SEE-based assessment is configured according to the
    course setup.
-   Coursework follows the normal Examination workflow after
    configuration.
-   Examination results are published through the existing result
    process.
-   Marks cards can be generated through the existing workflow.
-   Coursework results can be pushed to NAD when required.
-   SSP can consume coursework data when scholarship processing requires
    it.

### 3. R&D Phase 2 -- Synopsis

After coursework completion: 1. Passed students become available in the
R&D module. 2. Department Chairperson configures the synopsis submission
date/timeline. 3. Scholar submits the synopsis and supporting details.
4. The submission moves through Guide, Co-Guide (if assigned),
Department Chairperson and Doctoral Committee review. 5. Reviewers can
approve, reject or send back the submission with remarks/comments as
configured. 6. Pre-registered Colloquium/Symposium details can be
captured where applicable. 7. Once the synopsis is approved by the
Doctoral Committee, the scholar proceeds to the next stage.

### 4. Permanent USN / Ph.D scholar conversion

After synopsis approval: - University Admin can forward the provisional
USN for permanent-USN processing. - Superintendent approves and forwards
the request to Registrar (Admin). - Registrar (Admin) approves the
permanent USN. - The permanent USN is assigned and the student is
notified. - The student is then treated as a Ph.D scholar for the
subsequent R&D workflow.

### 5. R&D Phase 4 -- Progress reports

Department Chairperson configures scholar-wise progress-report frequency
from the start date.

Supported frequencies in the source workflow: - Bi-weekly - Monthly -
Three months - Six months - One year

Approval flow:

``` text
Scholar → Guide → Co-Guide (if assigned) → Department Chairperson → Doctoral Committee
```

Functionality includes: - Progress-report submission with additional
details. - Progress-report document upload. - Review remarks by Guide,
Co-Guide, Department Chairperson and Doctoral Committee as applicable. -
View of the current approval stage/status. - Send back/rejection with
comments where configured. - Submission enabled only during the
configured submission window. - Deadline-expired message after the
submission deadline. - Display of the next upcoming report and its
submission timeline after approval. - Progress Report ID and Final
Report ID generation using the configured admission year, university,
Area of Research/discipline short form and report number.

The process continues until the configured maximum Ph.D duration,
including applicable extension/maternity-leave periods.

### 6. Final thesis, Viva Voce / Colloquium / Symposium

When the final progress report/thesis is completed and approved: 1.
Doctoral Committee identifies the scholar for Final Viva Voce,
Colloquium or Symposium. 2. Panel of Examiners is configured. 3. Date,
time, duration and conduction mode are configured. 4. Venue/online link
and examiner details are captured. 5. Scholar receives the
invitation/schedule. 6. After the scheduled event, the Doctoral
Committee uploads required supporting details/documents. 7. Doctoral
Committee approves or rejects the final Viva Voce/Colloquium/Symposium.
8. Rejected scholars can be returned to the next-symposium/re-invitation
workflow.

Typical statuses: - Yet to Send - Scheduled - Yet to Upload Details -
Approved - Rejected

### 7. Registrar (Evaluation) and Ph.D convocation

-   Scholars whose final Viva Voce/Colloquium/Symposium is completed
    become available to Registrar (Evaluation).
-   Registrar (Evaluation) marks eligible scholars for convocation.
-   After the Ph.D convocation notification is configured, eligible
    scholars can apply using the applicable Indian/Foreign fee
    structure.
-   After fee payment, scholars appear in the Convocation Eligibility
    list.
-   PDC and Ph.D degree/convocation certificate printing are supported
    using formats supplied by the UUCMS SPMU team.

### 8. Scholar requests during the Ph.D lifecycle

The source workflow defines request flows for: - Guide change. -
Co-Guide allocation. - Co-Guide change. - Guide change under special
circumstances. - Co-Guide change under special circumstances. -
Guide/Co-Guide change based on special-circumstance master data and
applicable fee. - Change of mode of study: Fellowship/Full Time or
Non-Fellowship/Part Time. - Extension of expected end date. - Maternity
leave. - Additional year of extension.

The general approval route is:

``` text
Student → Guide/Co-Guide → Department Chairperson → Doctoral Committee
```

with participants varying by request type.

### 9. Faculty and Student Research Projects

The R&D module also contains a separate research-project workflow.

**University Admin / College Admin** - Creates research funding
agencies. - Creates Research Review Committees under Areas of
Research. - Maps eligible faculties to projects as Principal
Investigator (PI) or Mentor. - Configures Area of Research, Discipline
and related project setup. - Project/funding configuration is restricted
where the source workflow specifies that funding-agency information has
already been submitted to a funding project.

**Principal Investigator / Mentor** Creates a research project/proposal
with: - Project name and objective. - Project type. -
Funding/non-funding selection. - Internal/external funding type. -
Funding agency where applicable. - Estimated cost. - Cost
proposal/supporting documents where applicable. - Area of Research and
related project information.

Conditional behaviour: - For an Internal project, the external
funding-agency list is not loaded. - For a non-funding project, the
relevant cost/proposal fields are displayed according to the configured
workflow.

**Research project approval**

``` text
Principal Investigator / Mentor
        ↓
Research Review Committee
        ↓
Registrar (Admin)
        ↓
Vice Chancellor
```

At configured stages the project may be approved, rejected or sent back
with comments.

For funded projects: - Vice Chancellor selects the applicable HOA
through the Finance module. - The HOA is used for fund flow for
internal/external funding types. - Sanction letter is uploaded after
approval. - The project proceeds to the next stage.

**Project members and onboarding** - Project Fellowships - JRFs - SRFs -
Research Assistants - Permanent/Temporary Faculty - Contract workers -
Mentors - Students of all programme levels

Members are mapped with project role and remuneration. The
onboarding/login portion for Project Fellowships, JRFs, SRFs and
Research Assistants is identified in the source as an HRMS/out-of-SRS
dependency.

**Project progress** - PI/Mentor configures progress-report frequency:
bi-weekly, monthly, three months, six months or one year. - Project
members submit progress reports with supporting details. - PI/Mentor
reviews submissions and records member progress/completion. - Project
progress document upload is supported. - Final project report and
Utilization Certificate are submitted by the PI. - MoU upload and yearly
Utilization Certificate are supported where required.

**Research project closure**

``` text
Principal Investigator
      ↓
Research Review Committee
      ↓
Registrar (Admin)
      ↓
Vice Chancellor
```

Once the final report and required utilization/certification documents
are approved by the Vice Chancellor, the research project is considered
completed/closed. Universities can view research projects undertaken
during a particular academic year with their status.

### 10. R&D Playwright automation scope

The R&D functionality can use the same recording → POM → test-data
approach already used for Login and Exam.

``` text
R&D
├── Ph.D Admission / Eligibility
├── Guide & Co-Guide
├── Area of Research
├── Seat / Vacancy Matrix
├── Synopsis Submission & Approval
├── Permanent USN Approval
├── Progress Report Configuration
├── Scholar Progress Report Submission
├── Guide / Co-Guide / Chairperson / Doctoral Committee Review
├── Final Report / Thesis
├── Viva Voce / Colloquium / Symposium
├── Registrar (Evaluation) Convocation Eligibility
├── Scholar Requests
│   ├── Guide Change
│   ├── Co-Guide Allocation/Change
│   ├── Mode of Study Change
│   ├── Extension
│   └── Maternity Leave
└── Faculty / Student Research Projects
    ├── Funding Agency
    ├── Research Review Committee
    ├── Project Creation
    ├── Project Approval
    ├── Project Member Mapping
    ├── Project Progress Reports
    ├── Utilization Certificate
    └── Project Closure
```

Selectors, credentials, upload files, approval statuses and expected
messages should be captured from the actual UUCMS environment through
Playwright recording/inspection rather than guessed, because the
uploaded R&D source documents define workflows and UI requirements but
do not provide concrete DOM selectors.

### R&D Phase-1

Phase-1 automation covers the ADMISSION (program details),
AREAOFRESEARCH, FACULTYMAPPING, SYNOPSIS and PERMUSN test cases from
`testcases/rnd_phase-1_testcases.csv`.

Create the R&D test-data files from their templates:

``` powershell
Copy-Item test_data\rnd\admission_program_details.example.json test_data\rnd\admission_program_details.json
Copy-Item test_data\rnd\area_of_research.example.json test_data\rnd\area_of_research.json
Copy-Item test_data\rnd\faculty_mapping.example.json test_data\rnd\faculty_mapping.json
Copy-Item test_data\rnd\synopsis.example.json test_data\rnd\synopsis.json
Copy-Item test_data\rnd\permanent_usn.example.json test_data\rnd\permanent_usn.json
```

After recording each R&D flow, fill every `REPLACE_WITH_*` selector,
dropdown label/value, date, USN and file path in the matching
`test_data/rnd/*.json` file. Multi-role flows (synopsis approval chain,
permanent USN chain) switch logins through the `rnd_login` fixture:
add one entry per role (student, guide, coguide,
department_chairperson, doctoral_committee_chairperson, college_admin,
superintendent, registrar_admin, university_admin) under the
`roles` mapping in `test_data/login/LoginData.json` (see
`test_data/login/LoginData.example.json`). The configured default login in
`LoginData.json` should be the University Admin; it is used by the
`authenticated_page` fixture. The menu paths in
`src/uucms/constants/menu_paths/research_development.py` are documented from
the test cases - confirm each one against a recording.

Run only the R&D Phase-1 tests:

``` powershell
.venv\Scripts\python.exe -m pytest tests -k rnd -v
```

or the one-click runners `.\run_rnd.bat` / `.\scripts\run-rnd.ps1`.

The R&D tests intentionally stop with a clear error while their
test-data files still contain `REPLACE_WITH` placeholders. This
prevents guessed selectors from creating unreliable automation.

### R&D Ph.D setup (Academics screens)

The University Admin Ph.D setup is automated from the Academics menu
screens (Program Details, Areas of Research) plus Research And
Development > Set-up: map an Area of Research to the Ph.D program,
map/view/modify the Area of Research to faculty mapping, map the
student to the committee, and create the committee. The screen page
objects live under `src/uucms/modules/academics/pages/` while the
workflow lives under `src/uucms/workflows/research_development/`.

Create the Ph.D setup test-data file from its template:

``` powershell
Copy-Item test_data\rnd\phd_setup.example.json test_data\rnd\phd_setup.json
```

After recording each screen, fill every `REPLACE_WITH_*` selector and
value in `test_data/rnd/phd_setup.json`. The stages run as the
University Admin role from `test_data/login/LoginData.json`.

``` powershell
.venv\Scripts\python.exe -m pytest tests\ui\research_development\test_rnd_phd_setup.py -m rnd -v
```

### R&D Research Projects (Phase-3 screens)

The Research Projects sub-menu (top nav "Research And Development" >
"Research Projects") is automated for the Department Chairperson across
the four screens: Research Projects Details (list + Create Research
Project form), Submission Configuration, Submissions (View Details
modal) and Progress Completion. The screen page objects live under
`src/uucms/modules/research_development/pages/research_projects/`.

Create the Research Projects test-data file from its template:

``` powershell
Copy-Item test_data\rnd\research_projects.example.json test_data\rnd\research_projects.json
```

After recording each screen, fill every `REPLACE_WITH_*` selector and
value in `test_data/rnd/research_projects.json`. The screen-structure
tests (headings, breadcrumbs, filters, buttons, table columns,
empty-state text, create-form smoke check) run as soon as the file is
copied; the create-project, configuration, View Details modal and
completion-marking tests intentionally stop with a clear error while
their selectors still contain `REPLACE_WITH` placeholders, and the
row-level checks skip when the tables have no rows. Run only the
Research Projects tests:

``` powershell
.venv\Scripts\python.exe -m pytest tests -k rnd_rp -v
```

or the one-click runner `.\run_rnd_research_projects.bat` /
`.\scripts\run-rnd-research-projects.ps1`.

## AI agents (opencode)

Two project agents under `.opencode/agent/` drive the test-case and
automation workflow:

1. `testcase-writer` — turns requirement decks into test cases. Give it
   a raw PPTX path or an extracted `docs/rnd/*.md` file. It extracts the
   deck with `scripts/extract_pptx.py` when needed and writes
   `testcases/<module>_<slug>_testcases.csv` with TC-ID, steps, expected
   result, and an empty actual-result column to be filled after
   execution.
2. `playwright-writer` — turns the test case CSV into automation in this
   project's structure (page objects under `src/uucms/modules`, workflows
   under `src/uucms/workflows`, `test_data` JSON templates, UI tests under
   `tests/ui`, and unit tests under `tests/unit`).
   Unrecorded selectors stay as `REPLACE_WITH` placeholders until filled
   from a codegen recording.

Example flow:

``` text
@testcase-writer  write test cases for C:\...\Phase 2 R&D Module Final 1.pptx
@playwright-writer  automate testcases\rnd_phase-2_testcases.csv
```

The extracted deck sources live under `docs/rnd/`
(`phase-1.md`, `phase-2.md`, `phase-3.md`, `phase-2-master-v2.md`),
generated by:

``` powershell
.venv\Scripts\python.exe scripts\extract_pptx.py "<deck.pptx>" -o "docs\rnd\<slug>.md"
```
