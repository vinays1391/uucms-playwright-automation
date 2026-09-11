param(
    [switch]$Headed
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path ".env")) { Write-Warning "No .env file found; copy .env.example to .env and configure it." }
if ($Headed) { $env:UUCMS_HEADLESS = "false" }
$Python = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }
$Browser = "chromium"
if (Test-Path ".env") {
    $BrowserSetting = Select-String -Path ".env" -Pattern "^UUCMS_BROWSER\s*=\s*(.+)$" | Select-Object -First 1
    if ($BrowserSetting) { $Browser = $BrowserSetting.Matches[0].Groups[1].Value.Trim().ToLower() }
}
if ($Browser -notin @("chromium", "firefox", "webkit")) { throw "UUCMS_BROWSER must be chromium, firefox, or webkit." }
& $Python -m playwright install $Browser
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Python -m pytest tests/test_login.py -m login --browser=$Browser
exit $LASTEXITCODE
