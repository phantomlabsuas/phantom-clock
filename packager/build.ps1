# build.ps1 — run from anywhere, handles paths with special chars in R&D
param(
    [switch]$Console   # pass -Console to show a console window in the exe
)

$root    = (Resolve-Path "$PSScriptRoot\..").Path
$release = Join-Path $root "dist"
$work    = Join-Path $PSScriptRoot "build"

# Generate Windows version metadata from APP_VERSION in server.py
$genScript   = Join-Path $PSScriptRoot "gen_version.py"
$versionFile = Join-Path $PSScriptRoot "win_version_gen.txt"

python $genScript $root $versionFile
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to read version from server.py"; exit 1 }

$consoleFlag = if ($Console) { "-c" } else { "-w" }

Write-Host "[1/2] Installing dependencies..."
python -m pip install pyinstaller psutil --quiet

# Close phantom-clock.exe if running, otherwise PyInstaller cannot overwrite it
$proc = Get-Process -Name "phantom-clock" -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host "Stopping running phantom-clock.exe..."
    $proc | Stop-Process -Force
    Start-Sleep -Milliseconds 500
}

Write-Host "[2/2] Building phantom-clock.exe ..."
python -m PyInstaller `
    --onefile `
    $consoleFlag `
    "--add-data=$root\index.html;." `
    "--add-data=$root\single_instance.py;." `
    "--add-data=$root\config.json;." `
    --hidden-import psutil `
    "--distpath=$release" `
    "--workpath=$work" `
    "--specpath=$PSScriptRoot" `
    "--version-file=$versionFile" `
    --name phantom-clock `
    "$root\server.py"

Write-Host ""
$exe = Join-Path $release "phantom-clock.exe"
if (Test-Path $exe) {
    Write-Host "Done. Exe ready at: $exe"
} else {
    Write-Host "Build failed - check output above."
}
