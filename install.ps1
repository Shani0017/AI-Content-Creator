# AI Content Creator - one-command installer for Windows.
# Run in cmd:  powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/Shani0017/AI-Content-Creator/main/install.ps1 | iex"
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$Repo = "Shani0017/AI-Content-Creator"
$Dest = Join-Path $env:USERPROFILE "AI-Content-Creator"

function Say($m) { Write-Host ""; Write-Host "==> $m" -ForegroundColor Cyan }
function Have($c) { return [bool](Get-Command $c -ErrorAction SilentlyContinue) }

# ---- 1. Python 3.11 (3.15 / 3.14 have no packages for the speech tools yet, so we always use 3.11 or 3.12)
Say "Looking for Python 3.11 or 3.12"
function Find-Python {
    foreach ($v in "3.11", "3.12") {
        try { $p = & py "-$v" -c "import sys;print(sys.executable)" 2>$null; if ($p) { return $p.Trim() } } catch {}
    }
    foreach ($p in "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe", "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
                   "C:\Program Files\Python311\python.exe", "C:\Program Files\Python312\python.exe") {
        if (Test-Path $p) { return $p }
    }
    return $null
}
$Py = Find-Python
if (-not $Py) {
    if (-not (Have winget)) { throw "Python 3.11 is missing and winget is not available. Install Python 3.11 from https://www.python.org/downloads/release/python-3119/ and run this again." }
    Say "Installing Python 3.11 (this can take a minute)"
    winget install -e --id Python.Python.3.11 --scope user --accept-package-agreements --accept-source-agreements --silent
    $Py = Find-Python
    if (-not $Py) { throw "Python 3.11 was installed but not found. Close this window, open a new one and run the command again." }
}
Write-Host "Using $Py"

# ---- 2. the app
Say "Downloading the app to $Dest"
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
$zip = Join-Path $env:TEMP "aicc.zip"
Invoke-WebRequest -Uri "https://github.com/$Repo/archive/refs/heads/main.zip" -OutFile $zip
$tmp = Join-Path $env:TEMP "aicc_extract"
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
Expand-Archive -Path $zip -DestinationPath $tmp -Force
$src = Get-ChildItem $tmp | Select-Object -First 1
# copy over everything except the user's own folders
$keep = @(".venv", "data", "models", "output", "settings.json")
Get-ChildItem $src.FullName -Force | Where-Object { $keep -notcontains $_.Name } | ForEach-Object {
    Copy-Item $_.FullName -Destination $Dest -Recurse -Force
}
Remove-Item $zip, $tmp -Recurse -Force -ErrorAction SilentlyContinue

# ---- 3. virtual environment + packages
Say "Installing the video, voice and AI libraries (a few minutes)"
Set-Location $Dest
$VenvPy = Join-Path $Dest ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPy)) { & $Py -m venv .venv }
& $VenvPy -m pip install --upgrade pip --quiet
& $VenvPy -m pip install --prefer-binary --only-binary=:all: -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Package install failed. Check the internet connection and run the command again." }

# ---- 4. voice files (about 340 MB)
Say "Downloading the voice files (about 340 MB)"
& $VenvPy -m forge.setup_models

# ---- 5. Ollama (the local AI) + a small model
if (-not (Have ollama) -and -not (Test-Path "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe")) {
    if (Have winget) {
        Say "Installing Ollama (the local AI)"
        winget install -e --id Ollama.Ollama --accept-package-agreements --accept-source-agreements --silent
    } else {
        Write-Host "Please install Ollama from https://ollama.com (needed for AI-written problems and scripts)." -ForegroundColor Yellow
    }
}
$ollama = (Get-Command ollama -ErrorAction SilentlyContinue).Source
if (-not $ollama) { $ollama = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" }
if (Test-Path $ollama) {
    Say "Downloading the AI model llama3.2:3b (about 2 GB)"
    try { Start-Process -FilePath $ollama -ArgumentList "serve" -WindowStyle Hidden | Out-Null; Start-Sleep 4 } catch {}
    try { & $ollama pull llama3.2:3b } catch { Write-Host "Model download skipped. You can do it later from Settings in the app." -ForegroundColor Yellow }
}

# ---- 6. desktop shortcut and launch
Say "Creating the desktop shortcut"
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut((Join-Path ([Environment]::GetFolderPath("Desktop")) "AI Content Creator.lnk"))
$lnk.TargetPath = Join-Path $Dest "start.bat"
$lnk.WorkingDirectory = $Dest
$lnk.Save()

Say "All done. Starting the app..."
Start-Process -FilePath (Join-Path $Dest "start.bat") -WorkingDirectory $Dest
