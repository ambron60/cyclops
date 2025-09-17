# Cyclops Sticky Notes

Cyclops is a minimalist sticky-note desktop utility built with PyQt6. Every
note floats above other windows so quick reminders stay close at hand without
reaching for a browser or heavyweight productivity suite.

![Cyclops sticky notes screenshot](docs/screenshot.png "Cyclops notes")

> **Note**: The screenshot reference is optional—remove the image line or drop a
> PNG at `docs/screenshot.png` before publishing to keep the badge above from
> breaking.

## Features

- **Always-on-top stickies** – frameless windows you can drag and resize freely.
- **Per-note colors and opacity** – subtle vertical slider hugs the right edge
  so the control blends into the note while remaining easy to adjust.
- **Instant capture** – double-click the header, tap the new-note button, or use
  your platform’s native *New* shortcut (Ctrl+N on Windows/Linux, ⌘+N on macOS).
- **Resilient persistence** – saves to `~/.stickies/notes.json`, falls back to a
  temp directory when needed, and writes a `.bak` backup after each save for
  quick recovery.

## Prerequisites

- Python 3.11 or newer
- A virtual environment manager (recommended)

## Quick Start

```bash
git clone https://github.com/ambron60/cyclops.git
cd cyclops
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

## Building Standalone Apps

PyInstaller is not pinned in `requirements.txt`; install it in your active
environment when you need to create binaries.

```bash
pip install pyinstaller
pyinstaller Cyclops.spec
```

- **macOS** – The spec emits `dist/Cyclops.app`. Codesign (`codesign --deep …`)
  and notarize (`xcrun notarytool`) before distributing broadly.
- **Windows** – The same spec bundles PyQt6 dependencies and produces
  `dist\Cyclops\Cyclops.exe`. Sign with `signtool` if you want to avoid SmartScreen warnings.

## Storage & Backups

- Primary save path: `~/.stickies/notes.json`
- Fallback: a temp directory selected automatically if the home path is not
  writable (the app displays a warning dialog when this happens)
- On successful save, Cyclops writes both `notes.json` and a `notes.json.bak`
  you can restore manually if needed.

## Troubleshooting

- **“Storage Error” on launch** – Ensure your user has permission to create
  `~/.stickies` or adjust the temp directory permissions noted in the dialog.
- **Notes missing after a crash** – The application attempts to reload the
  `.bak` file automatically. If that fails, you can open the backup in a text
  editor and copy the note contents out manually.
- **PyInstaller build issues** – Try reinstalling PyInstaller inside the virtual
  environment and delete the `build/` and `dist/` directories before rebuilding.

## License

TBD

