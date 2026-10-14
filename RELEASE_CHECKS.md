# Release checks — v2.1.2

Performed locally on Windows x64 with Python 3.10.11, using a fresh isolated environment rather than the development machine's broad package collection.

- **35 automated tests passed** against the clean source. Tests cover parsing, named links, `//` normalization, notes in text, encrypted/multi-package extraction, exports, corrupt-input handling, worker success/failure, model editing/search/removal, suffix/overwrite settings, and clickable URL preservation. Browser launches and clipboard writes are mocked in tests.
- The public tests use only generic fixtures; no private source CSV or catalog is required.
- The rebuilt **one-directory Windows application** passed its packaged self-test: real online DLC creation, verification, decryption, CSV export, and TXT export.
- The packaged application's Qt offscreen UI smoke test passed, including bundled logos and control assets. This is not a claim of testing every interaction on every Windows system.
- Local private text/DLC examples were also exercised without downloading hosted files. Those input lists and containers are **not included**.
- The checked-in DLC was independently decrypted and checked: exactly three benign placeholder links on example.com/org/net.
- The finished MP4 was inspected with FFprobe: H.264, 1600×1080, 30 fps, **24.5 seconds**, silent. A contact sheet was generated from the encoded MP4 and visually reviewed. The demo performed real import, live decryption, and both export actions.
- The MP4/GIF/screenshots contain only the benign public example data. The video uses scripted real widgets and a presentation cursor overlay, not a personal desktop recording.

The final packaging step additionally checks ZIP integrity, required files, local Markdown links, SHA-256 checksums, and excluded/private content. These local packaging checks preceded GitHub publication. See [GitHub Actions](https://github.com/XD3V3LOP3RX/Linkforge/actions) for current Windows/Python 3.10 and 3.12 results, and [Releases](https://github.com/XD3V3LOP3RX/Linkforge/releases) for published assets. The executable is not code signed.

Windows CI checks compare file/directory identity rather than path spelling, because Qt may expand an 8.3 short path into its equivalent long form.

These checks do not guarantee host availability, permissions to download a particular URL, key-service uptime, universal Windows compatibility, or a third-party legal/security audit.
