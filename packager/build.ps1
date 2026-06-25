# build.ps1 — run from anywhere, handles paths with special chars in R&D
param(
    [switch]$Console   # pass -Console to show a console window in the exe
)

$root    = (Resolve-Path "$PSScriptRoot\..").Path
$work    = Join-Path $PSScriptRoot "build"

# Generate Windows version metadata from version.json
$genScript   = Join-Path $PSScriptRoot "gen_version.py"
$versionFile = Join-Path $PSScriptRoot "win_version_gen.txt"

python $genScript $root $versionFile
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to read version from version.json"; exit 1 }

$version = (Get-Content (Join-Path $root "version.json") | ConvertFrom-Json).version
$release = Join-Path $root "release\package\PhantomClock_$version"
New-Item -ItemType Directory -Force -Path $release | Out-Null

$consoleFlag = if ($Console) { "-c" } else { "-w" }

Write-Host "[1/2] Installing dependencies..."
python -m pip install pyinstaller psutil --quiet

# Close PhantomClock.exe if running, otherwise PyInstaller cannot overwrite it
$proc = Get-Process -Name "PhantomClock" -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host "Stopping running PhantomClock.exe..."
    $proc | Stop-Process -Force
    Start-Sleep -Milliseconds 500
}

Write-Host "[2/2] Building PhantomClock.exe ..."
python -m PyInstaller `
    --onefile `
    $consoleFlag `
    "--add-data=$root\resources\index.html;resources" `
    "--add-data=$root\config\config.json;config" `
    "--paths=$root\src\phantom_clock" `
    --hidden-import psutil `
    "--distpath=$release" `
    "--workpath=$work" `
    "--specpath=$PSScriptRoot" `
    "--version-file=$versionFile" `
    --name PhantomClock `
    "$root\src\phantom_clock\server.py"

Write-Host ""
$exe = Join-Path $release "PhantomClock.exe"
if (Test-Path $exe) {
    Write-Host "Done. Exe ready at: $exe"
} else {
    Write-Host "Build failed - check output above."
}
