# UUCMS Playwright Login

A separate Python/Playwright login automation project. It coexists with the existing Java/Selenium/TestNG UUCMS framework.

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -e .
py -m playwright install chromium
Copy-Item .env.example .env
Copy-Item test_data/loginData.example.json test_data/loginData.json
```

Set `username` and `password` in `test_data/loginData.json`. The `captcha` field is currently `12345`. Keep the URL, browser, headless mode, and timeout in `.env`. Set `UUCMS_BROWSER` to `chromium`, `firefox`, or `webkit`; the test, Codegen, video recorder, and one-click runner all use that value. The example uses `http://123.63.4.210:5010/`. Login data is ignored by Git.

## Codegen to POM workflow

1. Start with a normal login recording:

   ```powershell
   .\record_login.bat
   ```

2. Perform the login flow in the opened browser. Do not type real credentials if the generated recording will be shared; codegen can capture typed values.
3. Review the generated file under `recordings/`. Raw Python recordings are temporary and ignored by Git.
4. Paste the recording into `prompts/antigravity-pom-conversion.md` and use the documented Gemini-in-Antigravity prompt.
5. Review the returned selectors and waits, then apply only the maintained POM changes under `src/pages` and `tests`.
6. Run the maintained test with the one-click script:

   ```powershell
   .\run_login.bat
   .\scripts\run-login.ps1
   .\scripts\run-login.ps1 -Headed
   ```

The one-click runner installs Chromium when needed and executes the maintained test. It does not record a new flow or invoke AI conversion. Antigravity and Gemini are authoring tools only; the finished test runs locally.

## Exam module

Create the Exam test-data file from its template:

```powershell
Copy-Item test_data\createNotificationData.example.json test_data\createNotificationData.json
```

After recording the Exam workflow, enter every field selector and value, submit selector, and success selector in `test_data/createNotificationData.json`. Use `select_label` with one visible dropdown label, such as `2025-2026` or `regular`. Use `multiselect_labels` with comma-separated visible labels for custom multiselects, for example `Program One, Program Two`; use `fill` for text/date fields and `upload` for files. The test logs in using `loginData.json`, opens the Exam module, fills all configured fields, submits the form, and checks the configured success element. The raw Codegen file is removed after conversion because it can contain typed credentials; the video recording remains under `recordings/videos/`.

Run only the Exam test:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_exam.py -m exam -v
```

The Exam test intentionally stops with a clear error while `examData.json` still contains `REPLACE_WITH` placeholders. This prevents guessed selectors from creating unreliable automation.

## Video recording

To save a video of the browser session for future reference:

```powershell
.\record_login_video.bat
```

Complete the flow in the opened browser, then return to the terminal and press Enter. The `.webm` video is saved under `recordings/videos/`. Videos can contain credentials or other sensitive page data, so review them before sharing.

## CAPTCHA

This project accepts a configured CAPTCHA value through `UUCMS_CAPTCHA`, currently defaulted to `12345`. It does not attempt to solve or bypass visual CAPTCHA challenges. A test environment with a supported automation policy is required for unattended runs. If CAPTCHA is entered manually during recording, remove that value from the generated script before keeping it.

## Validation

The login test asserts that `#MenuDiv` is visible after submission. Failures retain Playwright traces and screenshots under `test-results/` without intentionally logging secret values.
