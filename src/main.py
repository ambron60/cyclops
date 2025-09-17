# main.py
from __future__ import annotations

# pip install PyQt6
import sys, json, random, tempfile, shutil
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QShortcut, QKeySequence, QColor
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPlainTextEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QColorDialog, QMessageBox, QSlider
)

SAVE_DIR = Path.home() / ".stickies"
SAVE_FILE = SAVE_DIR / "notes.json"
SAVE_LOCATION_WARNING: str | None = None
SAVE_LOCATION_ERROR: str | None = None


def _ensure_save_dir():
    """Try to create the preferred save directory; fall back if needed."""
    global SAVE_DIR, SAVE_FILE, SAVE_LOCATION_WARNING, SAVE_LOCATION_ERROR
    try:
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        return
    except PermissionError:
        reason = "permission denied"
    except OSError as exc:
        reason = str(exc)
    else:
        return

    fallback = Path(tempfile.gettempdir()) / "stickies"
    try:
        fallback.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        SAVE_LOCATION_ERROR = (
            f"Unable to create a writable notes directory.\n"
            f"Primary location: {SAVE_DIR}\nFailed with: {reason}\n"
            f"Fallback location: {fallback}\nFailed with: {exc}"
        )
        return

    SAVE_LOCATION_WARNING = (
        f"Could not use {SAVE_DIR} ({reason}). Notes will be saved in {fallback}."
    )
    SAVE_DIR = fallback
    SAVE_FILE = SAVE_DIR / "notes.json"


_ensure_save_dir()

DEFAULT_BG = QColor("#FFF79A")   # post-it yellow
HEADER_H = 30
FONT = QFont("Arial", 15)        # always black text

def clamp(v, lo, hi): return max(lo, min(hi, v))


class Sticky(QWidget):
    changed = pyqtSignal()     # text/pos/size/color/opacity changed
    closed = pyqtSignal(object)

    def __init__(self, manager, spawn_new_callback, initial=None):
        """
        initial: optional dict with keys x,y,w,h,text,bg,opacity
        opacity stored as float 0.1..1.0
        """
        super().__init__()
        self.manager = manager
        self.spawn_new_callback = spawn_new_callback
        self._drag_offset = None

        # STATE
        self.bg = DEFAULT_BG
        self.opacity = 1.0

        # WINDOW
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setMouseTracking(True)

        # ---- Header ----
        header = QFrame()
        header.setFixedHeight(HEADER_H)
        header.setStyleSheet(
            "background: rgba(0,0,0,0.06);"
            "border-top-left-radius:8px; border-top-right-radius:8px;"
        )
        h = QHBoxLayout(header)
        h.setContentsMargins(8, 4, 6, 4)

        # left side = drag area
        class DragArea(QWidget):
            def __init__(self, parent, spawn_new_callback):
                super().__init__(parent)
                self.spawn_new_callback = spawn_new_callback

            def mouseDoubleClickEvent(self, event):
                self.spawn_new_callback()

        drag_area = DragArea(self, self.spawn_new_callback)
        drag_area.setMinimumWidth(40)
        h.addWidget(drag_area, 1)

        # new
        new_btn = QPushButton("＋")
        new_btn.setFixedSize(26, 22)
        new_btn.setStyleSheet("border:none; background:transparent; font-weight:bold; color:black;")
        new_btn.clicked.connect(self.spawn_new_callback)
        h.addWidget(new_btn)

        # color
        color_btn = QPushButton("🎨")
        color_btn.setFixedSize(26, 22)
        color_btn.setStyleSheet("border:none; background:transparent;")
        color_btn.clicked.connect(self.pick_color)
        h.addWidget(color_btn)

        # close
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(26, 22)
        close_btn.setStyleSheet("border:none; background:transparent; font-weight:bold; color:black;")
        close_btn.clicked.connect(self.close)
        h.addWidget(close_btn)

        # ---- Editor ----
        self.editor = QPlainTextEdit()
        self.editor.setFrameStyle(0)
        self.editor.setFont(FONT)
        self.editor.setPlaceholderText("Type here…")
        self.editor.setStyleSheet("background:transparent; border:none; color:black;")
        self.editor.textChanged.connect(self.changed.emit)

        # ---- Opacity slider (right edge) ----
        self.slider = QSlider(Qt.Orientation.Vertical)
        self.slider.setRange(10, 100)          # 10% .. 100%
        self.slider.setValue(100)
        self.slider.setFixedWidth(10)          # keep control slim and unobtrusive
        self.slider.setStyleSheet("""
            QSlider {
                background: transparent;
                border: none;
            }
            QSlider::groove:vertical {
                background: rgba(0, 0, 0, 0.12);
                width: 2px;
                margin: 6px 4px;
                border-radius: 1px;
            }
            QSlider::sub-page:vertical {
                background: rgba(0, 0, 0, 0.08);
                border-radius: 1px;
            }
            QSlider::add-page:vertical {
                background: rgba(255, 255, 255, 0.25);
                border-radius: 1px;
            }
            QSlider::handle:vertical {
                background: rgba(0, 0, 0, 0.18);
                border: 1px solid rgba(255, 255, 255, 0.35);
                height: 12px;
                width: 12px;
                margin: -7px -5px;   /* slight overlap for easier grab */
                border-radius: 6px;
            }
            QSlider::handle:vertical:hover {
                background: rgba(0, 0, 0, 0.28);
            }
        """)
        self.slider.valueChanged.connect(self._on_slider_changed)

        # ---- Layout ----
        center = QVBoxLayout()
        center.setContentsMargins(6, 6, 6, 6)
        center.setSpacing(4)
        center.addWidget(header)
        center.addWidget(self.editor)

        root = QHBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)
        root.addLayout(center, 1)
        root.addWidget(self.slider, 0, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        # Double-click handled in DragArea subclass above
        # Shortcuts
        new_shortcut = QKeySequence(QKeySequence.StandardKey.New)
        shortcut = QShortcut(new_shortcut, self)
        shortcut.activated.connect(self.spawn_new_callback)
        new_btn.setToolTip(
            f"New note ({new_shortcut.toString(QKeySequence.SequenceFormat.NativeText)})"
        )
        # Double-click handled in DragArea subclass above

        # Geometry / content
        if initial:
            w = max(128, int(initial.get("w", 300)))
            hgt = max(128, int(initial.get("h", 300)))
            self.resize(w, hgt)
            self.move(int(initial.get("x", 140)), int(initial.get("y", 140)))
            self.editor.setPlainText(initial.get("text", ""))
            self.bg = self._hex_to_color(initial.get("bg", DEFAULT_BG.name()))
            self.opacity = clamp(float(initial.get("opacity", 1.0)), 0.1, 1.0)
            self.slider.setValue(int(round(self.opacity * 100)))
        else:
            self.resize(256, 256)
            self.move(140 + random.randint(-120, 120), 140 + random.randint(-120, 120))
            self.opacity = 1.0
            self.slider.setValue(100)

        self._apply_colors()
        self.setWindowOpacity(self.opacity)
        self.show()

    # --- UI handlers ---
    def _on_slider_changed(self, val: int):
        self.opacity = clamp(val / 100.0, 0.1, 1.0)
        self.setWindowOpacity(self.opacity)
        self.changed.emit()

    def pick_color(self):
        c = QColorDialog.getColor(self.bg, self, "Choose note color")
        if c.isValid():
            self.bg = c
            self._apply_colors()
            self.changed.emit()

    # --- Helpers ---
    def _apply_colors(self):
        self.setStyleSheet(
            "QWidget {"
            f"  background:{self.bg.name()};"
            "  border:1px solid #7a7a7a; border-radius:8px;"
            "}"
        )
        self.editor.setStyleSheet("background:transparent; border:none; color:black;")

    def _hex_to_color(self, s: str) -> QColor:
        q = QColor(s)
        return q if q.isValid() else DEFAULT_BG

    # --- Dragging on header strip ---
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and e.position().y() <= HEADER_H + 8:
            self._drag_offset = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.raise_()

    def mouseMoveEvent(self, e):
        if self._drag_offset and (e.buttons() & Qt.MouseButton.LeftButton):
            self.move(e.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, e):
        if self._drag_offset is not None:
            self.changed.emit()  # position changed
        self._drag_offset = None

    def resizeEvent(self, e):
        self.changed.emit()
        return super().resizeEvent(e)

    def closeEvent(self, event):
        self.closed.emit(self)
        super().closeEvent(event)

    # Serialize
    def to_dict(self) -> dict:
        return {
            "x": self.x(), "y": self.y(),
            "w": self.width(), "h": self.height(),
            "text": self.editor.toPlainText(),
            "bg": self.bg.name(),
            "opacity": self.opacity,
        }


class StickyManager:
    def __init__(self, app):
        self.app = app
        self.notes: list[Sticky] = []
        self._save_timer = QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._save_to_disk)

        if SAVE_FILE.exists():
            self._restore()
            if not self.notes:
                self.spawn_note()
        else:
            self.spawn_note()

    # Spawning
    def spawn_note(self):
        note = Sticky(self, self.spawn_note)
        note.changed.connect(self._save_debounced)
        note.closed.connect(self._on_note_closed)
        self.notes.append(note)
        self._save_debounced()

    def _spawn_from_dict(self, item: dict):
        note = Sticky(self, self.spawn_note, initial=item)
        note.changed.connect(self._save_debounced)
        note.closed.connect(self._on_note_closed)
        self.notes.append(note)

    # Closing
    def _on_note_closed(self, note):
        try:
            self.notes.remove(note)
        except ValueError:
            pass
        if self.notes:
            self._save_debounced()
        else:
            self._save_to_disk()
            self.app.quit()

    # Saving
    def _save_debounced(self, delay_ms=200):
        self._save_timer.start(delay_ms)

    def _save_to_disk(self):
        try:
            data = {"notes": [n.to_dict() for n in self.notes]}
            tmp_path = SAVE_FILE.with_name(SAVE_FILE.name + ".tmp")
            backup_path = SAVE_FILE.with_name(SAVE_FILE.name + ".bak")

            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            tmp_path.replace(SAVE_FILE)
            shutil.copy2(SAVE_FILE, backup_path)
        except Exception as e:
            QMessageBox.critical(None, "Save Error", str(e))

    def _restore(self):
        def _load_from(path: Path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data.get("notes", []):
                self._spawn_from_dict(item)

        try:
            _load_from(SAVE_FILE)
        except FileNotFoundError:
            return
        except Exception as exc:
            backup_path = SAVE_FILE.with_name(SAVE_FILE.name + ".bak")
            QMessageBox.warning(
                None,
                "Load Error",
                "Could not read saved notes ({}).\n\nAttempting to restore the last backup.".format(exc),
            )
            if backup_path.exists():
                try:
                    _load_from(backup_path)
                    QMessageBox.information(
                        None,
                        "Backup Restored",
                        f"Notes were restored from {backup_path}.",
                    )
                except Exception as backup_exc:
                    QMessageBox.critical(
                        None,
                        "Restore Error",
                        f"Failed to restore notes from backup: {backup_exc}",
                    )
            else:
                QMessageBox.critical(
                    None,
                    "Restore Error",
                    "No backup was available. A new note will be created.",
                )


def main():
    app = QApplication(sys.argv)
    # Consistent cross-platform look; no native menus used.
    app.setStyle("Fusion")
    if SAVE_LOCATION_ERROR:
        QMessageBox.critical(None, "Storage Error", SAVE_LOCATION_ERROR)
        return 1

    StickyManager(app)

    if SAVE_LOCATION_WARNING:
        QMessageBox.warning(None, "Storage Warning", SAVE_LOCATION_WARNING)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
