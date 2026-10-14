# Changelog

Notable behavior and release information for LinkForge Studio. This file does not claim a history for versions not documented here.

## 2.1.2

### Release scope

- Portable Windows x64 desktop interface built with PySide6 / Qt.
- Standard JDownloader DLC creation and link extraction, including multi-package imports.
- DLC, CSV, and TXT import, paste input, and file drag and drop.
- CSV export with `Title,Package,Link` and TXT export with URLs.
- Original encoded URLs preserved for opening, copying, and export; decoded display only.
- Deduplication by URL, name, and package; view filters do not limit exports.
- Recompilation into one chosen package and a 64 MB DLC input safety limit.
- Illustrative placeholder examples and demo media, plus clean-repository development and build instructions.

### Important constraints

Creating, decrypting, and verifying DLC requires the fixed online JDownloader key service. Only the container key/token—not plaintext link lists—is sent to the key service. DLC is not a private vault.

LinkForge does not download files itself. Opening a URL delegates to the default browser and may initiate a download. It does not check destination compatibility or archive contents, bypass CAPTCHAs, or embed archive passwords.

See [RELEASE_NOTES.md](RELEASE_NOTES.md) for a release-body draft and [SECURITY.md](SECURITY.md) for security guidance.
