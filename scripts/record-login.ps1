param(
    [string]$Url = $(if ($env:UUCMS_BASE_URL) { $env:UUCMS_BASE_URL } else { "http://123.63.4.210:5010/" }),
    [string]$Output = "recordings\login_codegen.py"
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Output) | Out-Null
$Python = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }
$Browser = "chromium"
if (Test-Path ".env") {
    $BrowserSetting = Select-String -Path ".env" -Pattern "^UUCMS_BROWSER\s*=\s*(.+)$" | Select-Object -First 1
    if ($BrowserSetting) { $Browser = $BrowserSetting.Matches[0].Groups[1].Value.Trim().ToLower() }
}
if ($Browser -notin @("chromium", "firefox", "webkit")) { throw "UUCMS_BROWSER must be chromium, firefox, or webkit." }
& $Python -m playwright codegen --browser=$Browser --target=python --output=$Output $Url
exit $LASTEXITCODE
