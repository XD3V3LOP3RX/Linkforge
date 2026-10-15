# Third-party notices

The [MIT license](LICENSE) covers original LinkForge code and artwork only. The Windows release also includes the following unmodified runtime components, which retain their own licenses. Applicable texts/notices are preserved together in [THIRD_PARTY_LICENSES.txt](THIRD_PARTY_LICENSES.txt).

| Component | Release version | License |
| --- | --- | --- |
| Python | 3.10.11 | Python Software Foundation license and included notices |
| Qt / PySide6 Essentials / Shiboken6 | 6.9.0 | LGPLv3 open-source option |
| requests | 2.34.2 | Apache-2.0 |
| urllib3 | 2.8.0 | MIT |
| idna | 3.20 | BSD-3-Clause |
| charset-normalizer | 3.5.2 | MIT |
| certifi / Mozilla CA bundle | 2026.7.22 | MPL-2.0 |
| PyCryptodome | 3.22.0 | BSD and public-domain portions |

Qt includes additional third-party code covered by the attribution documentation and corresponding upstream source. Do not remove applicable notices when redistributing or rebuilding.

## Qt shared libraries

This app uses the LGPLv3 open-source licensing option, not a commercial Qt subscription. The full LGPLv3 and GPLv3 terms are included in the [dependency license texts](THIRD_PARTY_LICENSES.txt).

Keep `_internal/` beside the EXE. Compatible Qt/PySide6/Shiboken shared libraries can be replaced, and the included application source can be rebuilt against modified compatible libraries. LinkForge does not prohibit modification or reverse engineering for debugging those modifications. No signing or technical lock prevents replacement. Modified libraries must be distributed in accordance with their licenses, including corresponding-source requirements where applicable.

Upstream source and licensing:

- Qt for Python: https://code.qt.io/cgit/pyside/pyside-setup.git/ (6.9.0).
- Qt: https://code.qt.io/ (6.9.0 source repositories).
- Qt licensing: https://www.qt.io/licensing/.
- Python: https://www.python.org/downloads/source/.
- Other packages: upstream source links in their PyPI release metadata.

## Packager

PyInstaller 6.22.3 is used to produce the Windows bundle. Its bootloader redistribution exception and license are preserved in [the consolidated license texts](THIRD_PARTY_LICENSES.txt).

This document describes attribution and packaging; it is not legal advice.
