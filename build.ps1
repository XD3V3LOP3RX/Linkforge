$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path '.build-env\Scripts\python.exe')) {
        python -m venv .build-env
        if ($LASTEXITCODE -ne 0) { throw 'Could not create isolated build environment.' }
    }
    $python = '.build-env\Scripts\python.exe'
    & $python -m pip install -r requirements-build.txt
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
    & $python make_ui_assets.py
    if ($LASTEXITCODE -ne 0) { throw 'Artwork generation failed.' }
    & $python -m unittest test_core test_container_io test_qt_app -v
    if ($LASTEXITCODE -ne 0) { throw 'Regression tests failed.' }
    & $python -m PyInstaller --noconfirm --clean --onedir --windowed --name 'LinkForge Studio' --icon logo.ico --version-file version_info.txt --add-data 'logo.ico;.' --add-data 'logo.png;.' --add-data 'check.png;.' --add-data 'chevron.png;.' --exclude-module tkinter --exclude-module PyQt5 --exclude-module PyQt6 qt_app.py
    if ($LASTEXITCODE -ne 0) { throw 'Executable build failed.' }
    $destination = Join-Path $PSScriptRoot 'dist\LinkForge Studio'
    Copy-Item LICENSE,THIRD_PARTY_NOTICES.md -Destination $destination -Force
    Copy-Item LICENSES -Destination $destination -Recurse -Force
    Write-Host 'Ready: dist\LinkForge Studio\LinkForge Studio.exe'
    Write-Host 'Keep _internal alongside the EXE. Zip the whole folder for distribution.'
} finally {
    Pop-Location
}
