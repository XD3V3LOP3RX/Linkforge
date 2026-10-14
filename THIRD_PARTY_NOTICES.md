# Third-party notices

The MIT license in this repository covers original LinkForge code and artwork only. It does not relicense Python, Qt, PySide6, or other dependencies. Original package license/notice documents are included under `LICENSES/`; `DEPENDENCIES.json` records the versions used for this release.

## Runtime components

| Component | Release version | License |
| --- | --- | --- |
| Python | 3.10.11 | Python Software Foundation license and included notices |
| Qt / PySide6 Essentials | 6.9.0 | Open-source LGPLv3 option; see below |
| Shiboken6 | 6.9.0 | Open-source LGPLv3 option |
| requests | 2.34.2 | Apache-2.0 |
| urllib3 | 2.8.0 | MIT |
| idna | 3.20 | BSD-3-Clause |
| charset-normalizer | 3.5.2 | MIT |
| certifi / Mozilla CA bundle | 2026.7.22 | MPL-2.0 |
| PyCryptodome | 3.22.0 | BSD and public-domain portions; see its license |

These are unmodified upstream distributions. Qt contains additional third-party code under the licenses described in Qt's upstream attribution documentation and source distribution. Do not remove their notices when redistributing or rebuilding.

## Qt and LGPL

This release uses the **LGPLv3 open-source option**, not a commercial Qt license. Some upstream wheels include a commercial-license-option text; its presence does not mean this release has or requires a commercial Qt subscription. Full LGPLv3 and GPLv3 license texts are included in `LICENSES/LGPL-3.0.txt` and `LICENSES/GPL-3.0.txt`.

The Windows release uses an external shared-library layout (`_internal/`), not a single permanently embedded Qt library. Keep that folder alongside the EXE. You may replace compatible Qt/PySide6/Shiboken shared libraries, or rebuild the included MIT-licensed application source against a modified compatible library. LinkForge imposes no prohibition on modification or reverse engineering for debugging those library modifications. No code signing or technical lock prevents replacement.

Upstream source and licensing information:

- Qt for Python / PySide: https://code.qt.io/cgit/pyside/pyside-setup.git/ (release 6.9.0).
- Qt: https://code.qt.io/ (QtBase and associated 6.9.0 source repositories).
- Qt license overview: https://www.qt.io/licensing/.
- Python source: https://www.python.org/downloads/source/.
- Other runtime packages: source links in their PyPI distribution metadata; exact release versions are recorded above and in `DEPENDENCIES.json`.

If distributing a modified Qt library, comply with that library's license and provide its corresponding source as required. This document is an attribution and packaging explanation, not legal advice.

## Build and demo tools

PyInstaller 6.22.3 uses GPLv2-or-later with a special exception for generated application bundles; its bootloader exception and notices are included. The hooks package, setuptools, and Pillow notices are also preserved. Pillow 12.3.0 is used for original artwork and demo production, not the application's core workflow. FFmpeg is an external demo-generation tool, **not included in the application or ZIP**; its licensing depends on the locally installed build. The resulting original silent MP4/GIF has no third-party music, footage, or fonts embedded as separately distributed font files.
