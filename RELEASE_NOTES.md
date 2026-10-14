# LinkForge Studio v2.1.2

A portable Windows x64 desktop tool for turning named HTTP/HTTPS link lists into standard JDownloader DLC containers and extracting links from existing containers. Built with PySide6 / Qt; not affiliated with JDownloader.

## Download and run

Download **LinkForge-v2.1.2-windows-x64.zip** from the project's Releases, extract the **entire ZIP**, and double-click **LinkForge Studio.exe**. Keep `_internal/` next to the executable; do not move the executable alone. The portable release does not require Python.

The executable is unsigned. Windows SmartScreen may warn; only proceed if you trust the ZIP's source.

## Highlights

- Import `.dlc`, `.csv`, and `.txt`, paste text, or drag and drop files.
- Extract links across multiple DLC packages, or recompile imported entries into one chosen package.
- Export CSV (`Title,Package,Link`) or TXT URLs.
- Preserve original encoded URLs for opening, copying, and exporting; decoding affects display only.
- Deduplicate by URL, name, and package. View filters do not limit exported data.
- Ignore notes in arbitrary text, normalize `//` URLs to HTTPS, and recognize `Name | URL` for plain-text names.
- Apply a 64 MB DLC input safety limit.

[Overview](media/overview.png) · [Animated demo](media/demo.gif) · [Video demo](media/demo.mp4)

The media and checked-in samples use illustrative placeholder URLs on `example.com`, `example.org`, and `example.net`, not real archive downloads.

## Before you use it

- LinkForge does **not** download files itself. Clicking a blue URL opens it in your default browser and may initiate a download.
- Creating, decrypting, and verifying DLC requires `https://service.jdownloader.org/dlcrypt/service.php`. Only the container key/token—not plaintext link lists—is sent to the key service.
- DLC is **not a private vault**. Do not publish sensitive links or tokens.
- No private catalogs, destination compatibility checks, CAPTCHA bypass, or archive-content checks are provided. Archive passwords are not embedded.

## Source and licensing

Original application code is MIT licensed, copyright © 2026 LinkForge contributors; the entire dependency stack is not MIT licensed. Qt/PySide6 and other dependencies have their own licenses; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [LICENSES/](LICENSES/). Qt shared libraries remain replaceable in the one-directory bundle, and the source can be rebuilt with replacement Qt/PySide6 libraries, subject to licensing and compatibility.

See the [README](README.md) for Python 3.10+ development, tests, and clean-repository build instructions, and [SECURITY.md](SECURITY.md) for safe handling guidance.
