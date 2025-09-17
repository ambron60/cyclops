Cyclops Sticky Notes
====================

Cyclops is a lightweight sticky-note utility built with PyQt6. Each sticky is a
frameless floating window that stays on top, so quick reminders stay visible
without cluttering your desktop or tray menus.

Features
- Create, move, and resize as many notes as you need; each note remembers its
  position, size, and contents between sessions.
- Post-it inspired palette with an inline color picker for per-note themes.
- Vertical opacity slider on every note that blends into the edge of the sticky,
  keeping the control discreet while still easy to tweak.
- Keyboard shortcut uses your platform’s native "New" key combo (Ctrl+N on
  Windows/Linux, Command+N on macOS).

Requirements
- Python 3.11+
- PyQt6 (installed automatically via `requirements.txt`)

Setup
1. Create and activate a virtual environment (recommended):
   ```
   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

Run
```
python src/main.py
```

Storage
- Notes are saved to `~/.stickies/notes.json`.
- If that location is not writable, the app falls back to a temporary
  directory (you’ll see a warning dialog). A `.bak` backup is written after
  every successful save to guard against corruption.

Shortcuts and Tips
- Use the "＋" button, the native new-note shortcut, or double-click the header
  drag area to spawn another note.
- Drag the translucent header strip to move a note; resize from any edge.
- The slider on the right controls window opacity (10% to 100%).
- Closing the last note exits the application.

Troubleshooting
- **Can’t write to the save file** – You’ll see an error dialog if the app
  cannot find any writable directory. Grant write access to `~/.stickies` or
  update permissions on the fallback directory noted in the dialog.
- **Notes disappeared after a crash** – The app attempts to restore the latest
  backup (`notes.json.bak`). If recovery fails, that error is reported so you
  can inspect the backup file manually.

License
- TBD
