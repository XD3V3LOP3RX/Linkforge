# Contributing to LinkForge Studio

Contributions that improve generic link handling, DLC interoperability, accessibility, tests, and documentation are welcome. Keep examples benign and changes focused.

## Set up

Use Python 3.10+ in a clean checkout:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-build.txt
python qt_app.py
```

No external online accounts are required for development or building. Dependency installation may need network access; DLC creation, decryption, and verification require the online key service.

## Test and build

```powershell
python -m unittest test_core test_container_io test_qt_app -v
.\build.ps1
```

The PyInstaller one-directory build writes `dist/LinkForge Studio/LinkForge Studio.exe` and adjacent `_internal/` dependencies in this repository. Package the entire output folder so Qt shared libraries remain replaceable; do not distribute the executable alone. Rebuilding from source also permits replacement Qt/PySide6 libraries, subject to licensing and compatibility. Packaging the portable release ZIP is a separate step. Do not commit virtual environments, build outputs, executables, ZIPs, or runtime self-test artifacts.

## Changes and pull requests

- Describe the problem, proposed behavior, and checks you actually ran. Distinguish offline checks from tests that contact the key service.
- Add or update regression tests for changes to parsing, container handling, URL preservation, or exports.
- Preserve original encoded URLs for browser opening, copying, and export; decoded values are display-only.
- Keep filtering separate from export scope. Deduplication uses URL, name, and package.
- Preserve the 64 MB DLC input safety limit and the fixed HTTPS key-service endpoint.
- Use reserved example domains (`example.com`, `example.org`, `example.net`) in tests, screenshots, and demos. Do not add real archive-download links or sensitive tokens.
- Do not add private catalogs, CAPTCHA bypass, archive-content checks, or embedded archive passwords.
- Document dependency and licensing changes. Third-party licenses remain separate from the source's MIT license.

For a normal bug report, include the version, Windows version, reproducible steps, expected result, and a sanitized example. Never attach sensitive link lists, DLC tokens, or private URLs. For suspected vulnerabilities, follow [SECURITY.md](SECURITY.md) rather than posting exploit details publicly.

Contributions must be compatible with the project's [MIT License](LICENSE). Do not submit material you lack permission to redistribute.
