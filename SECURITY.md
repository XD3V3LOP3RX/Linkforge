# Security

## Security expectations

LinkForge Studio is provided **without warranty**, including any security warranty, under the [MIT License](LICENSE). No security audit, code-signing status beyond the unsigned release, or guaranteed response time is implied.

A DLC container is **not a private vault**. Treat link lists, containers, exported files, access tokens, and URLs with embedded credentials as sensitive. Do not publish them in issues, pull requests, logs, screenshots, or demo recordings.

## Network and browser behavior

DLC creation, decryption, and verification require the fixed HTTPS endpoint:

`https://service.jdownloader.org/dlcrypt/service.php`

LinkForge sends only the container key/token to this key service, not plaintext link lists. This is an external service whose availability and operation are outside this project's control. Do not infer privacy guarantees for DLC from its encoding or encryption.

LinkForge does not download files itself. Clicking a blue URL opens the original encoded URL in the default browser; the destination may initiate a download or present unsafe content. Decoded URLs are displayed for readability only, while opening, copying, and exporting preserve the original encoded URL.

## Safe handling

- Import only files and links you trust. The 64 MB DLC input safety limit is a resource guard, not proof that a container is safe.
- Review destinations before opening them. LinkForge does not verify link availability, destination compatibility, or archive contents.
- Do not assume CAPTCHA bypass or password handling: neither is provided, and archive passwords are not embedded.
- Portable releases are unsigned. Evaluate the source of a ZIP before proceeding past a SmartScreen warning; do not disable system protection globally.
- Keep Windows, Python (when running from source), and dependencies current.

## Reporting a suspected vulnerability

Do not disclose sensitive data or actionable exploit details in a public issue. If the repository offers GitHub private vulnerability reporting, use that channel. Otherwise, post only a minimal, non-sensitive request for a private reporting channel and wait for maintainers to provide one before sharing details.

Include the affected version, impact, reproducible steps, and a benign minimized example through the private channel. Redact credentials, personal information, real link lists, and service tokens. No security email, private reporting account, response deadline, or supported-version commitment is designated here.
