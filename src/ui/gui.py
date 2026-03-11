import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,
    QLabel, QHBoxLayout, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QIcon, QTextCharFormat, QColor, QFont, QSyntaxHighlighter, QTextCursor

script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, '..', '..', 'src')
sys.path.insert(0, src_dir)

try:
    from util.csvjson import merge_csv_to_json
except ModuleNotFoundError:
    sys.exit(1)

USER_FOLDER = os.path.join(script_dir, 'user')  
SAVE_PATH = os.path.join(USER_FOLDER, 'save.sve') 

class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.rules = []

        key = QTextCharFormat()
        key.setForeground(QColor("#86C7ED"))
        key.setFontWeight(QFont.Weight.Bold)
        self.rules.append((QRegularExpression(r'"([^"\\]|\\.)*"\s*:'), key))

        string = QTextCharFormat()
        string.setForeground(QColor("#A3D39C"))
        self.rules.append((QRegularExpression(r'"([^"\\]|\\.)*"'), string))

        number = QTextCharFormat()
        number.setForeground(QColor("#F4A261"))
        self.rules.append((QRegularExpression(r'-?\b\d+(\.\d+)?([eE][+-]?\d+)?\b'), number))

        literal = QTextCharFormat()
        literal.setForeground(QColor("#D4A5A5"))
        literal.setFontWeight(QFont.Weight.Bold)
        for w in ['true', 'false', 'null']:
            self.rules.append((QRegularExpression(r'\b' + w + r'\b'), literal))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)


class JsonEditor(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighter = JsonHighlighter(self.document())
        self.setFont(QFont("Consolas", 14))
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance('    '))
        self.setPlaceholderText("JSON will appear here after loading or converting…")
        self.setAcceptDrops(True)
        self.setReadOnly(True)
        self.set_locked_colors()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab and not self.isReadOnly():
            cursor = self.textCursor()
            cursor.insertText("    ")
            event.accept()
        else:
            super().keyPressEvent(event)

    def set_locked_colors(self):
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(40, 40, 40))
        palette.setColor(self.foregroundRole(), QColor(120, 120, 120))
        self.setPalette(palette)

    def set_unlocked_colors(self):
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(37, 37, 37)) 
        palette.setColor(self.foregroundRole(), QColor(212, 212, 212))
        self.setPalette(palette)

    def search_in_json(self, term):
        regex = QRegularExpression(term)
        cursor = self.textCursor()
        document = self.document()

        cursor.setPosition(0)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfDocument)
        cursor.select(QTextCursor.SelectionType.Document)

        document.setDefaultTextOption(cursor.document().defaultTextOption())
        match = regex.globalMatch(cursor.document().toPlainText())

        while match.hasNext():
            m = match.next()
            cursor.setPosition(m.capturedStart(), QTextCursor.MoveMode.KeepAnchor)
            cursor.setPosition(m.capturedEnd(), QTextCursor.MoveMode.KeepAnchor)
            cursor.setCharFormat(self.get_highlight_format())
            self.setTextCursor(cursor)

    def get_highlight_format(self):
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("#00FFD544"))
        return highlight_format


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV → JSON")
        self.resize(900, 900)
        self.setMinimumSize(800, 800)
        self.setMaximumSize(1920,1080)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.abspath(__file__)) 

        icon_path = os.path.join(project_root, '..', 'util', 'icon.ico')

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Icon not found at {icon_path}")

        self.json_path = None
        self.edited = False
        self.last_dir, self.last_json_dir = self.load_last_dirs() 

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)

        self.editor = JsonEditor()
        self.editor.textChanged.connect(self.mark_edited)
        splitter.addWidget(self.editor)

        splitter.setSizes([60, 80])
        layout.addWidget(splitter)

        self.status = QLabel("Ready")
        layout.addWidget(self.status)

        btns = QHBoxLayout()
        btns.setSpacing(12)

        for txt, cb, color in [
            ("Convert CSVs", self.convert_folder, "#4a90e2"),
            ("Load JSON", self.load_json, "#a650c8"),
            ("Unlock Edit", self.toggle_edit, "#e74c3c"),
            ("Save", self.save_edited, "#f39c12"),
        ]:
            b = QPushButton(txt)
            b.setFixedSize(100, 30)
            b.setStyleSheet(f"background: {color}; color: white; border-radius: 5px;")
            b.clicked.connect(cb)
            btns.addWidget(b)

        self.edit_btn = btns.itemAt(2).widget()
        layout.addLayout(btns)

        self.setStyleSheet("""
            QWidget {
                background: #1e1e1e;
                color: #e0e0e0;
                font-family: "System";
            }
            QTextEdit {
                background: #252526;
                color: #d4d4d4;
                font-family: Consolas, monospace;
                font-size: 14px;
                border: 1px solid #3a3a3a;
                selection-background-color: #264f78;
            }
            QListWidget {
                background: #252526;
                border: 1px solid #3a3a3a;
                selection-background-color: #094e8c;
            }
            QSplitter::handle {
                background: #333;
                height: 5px;
            }
            QLabel { color: #aaa; }
            QPushButton:hover { brightness(1.15); }
        """)

    def convert_folder(self):
        # Set default folder to last used directory (CSV folder)
        folder = QFileDialog.getExistingDirectory(self, "Select folder with CSVs", self.last_dir)
    
        if not folder:  # User canceled folder selection
            return
    
        # Save the selected folder as the last used directory
        self.last_dir = folder
        self.save_last_dirs(self.last_dir, self.last_json_dir)  # Save the folder for future use
    
        # Ask user where to save the output JSON file
        out, _ = QFileDialog.getSaveFileName(self, "Convert", self.last_json_dir, "JSON (*.json)")
    
        if not out:  # User canceled save
            return
    
        self.status.setText("Merging…")
        QApplication.processEvents()
    
        try:
            merge_csv_to_json(folder, out)  # Merge CSV to JSON
            self.status.setText(f"Saved: {os.path.basename(out)}")
            self.update_file_list(folder)  # Update file list with saved JSONs
        except Exception as e:
            self.status.setText(f"Error: {e}")

    def update_file_list(self, folder):
        self.file_list.clear()
        for name in sorted(os.listdir(folder)):
            if name.lower().endswith('.json'):
                self.file_list.addItem(name)

    def load_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open JSON", self.last_json_dir, "JSON (*.json)")
        if path:
            self._load_json(path)
            self.last_json_dir = os.path.dirname(path)  # Update last JSON save directory
            self.save_last_dirs(self.last_dir, self.last_json_dir)  # Save both paths

    def _load_json(self, path):
        try:
            with open(path, encoding='utf-8') as f:
                text = f.read()
            self.editor.setText(text)
            self.json_path = path
            self.edited = False
            self.editor.setReadOnly(True)
            self.editor.set_locked_colors()
            self.status.setText(f"Loaded: {os.path.basename(path)}")
        except Exception as e:
            self.status.setText(f"Load failed: {e}")

    def toggle_edit(self):
        ro = self.editor.isReadOnly()
        self.editor.setReadOnly(not ro)
        if self.editor.isReadOnly():
            self.edit_btn.setText("Unlock Edit")
            self.edit_btn.setStyleSheet("background: #e74c3c; color: white; border-radius: 5px;")
            self.editor.set_locked_colors()
        else:
            self.edit_btn.setText("Lock Edit")
            self.edit_btn.setStyleSheet("background: #27ae60; color: white; border-radius: 5px;")
            self.editor.set_unlocked_colors()

    def save_edited(self):
        if not self.json_path:
            self.status.setText("No file loaded")
            return
        if not self.edited:
            self.status.setText("No changes")
            return
        path = f"{os.path.splitext(self.json_path)[0]}-edited.json"
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.status.setText(f"Saved: {os.path.basename(path)}")
            self.edited = False
        except Exception as e:
            self.status.setText(f"Save failed: {e}")

    def mark_edited(self):
        if not self.edited:
            self.edited = True

    def load_last_dirs(self):
        os.makedirs(USER_FOLDER, exist_ok=True)  
        if os.path.exists(SAVE_PATH):
            try:
                with open(SAVE_PATH, encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('last_dir', ''), data.get('last_json_dir', '')
            except Exception as e:
                print(f"Error loading last directories: {e}")
        return '', ''  # Return empty if no saved dirs

    def save_last_dirs(self, folder, json_folder):
        os.makedirs(USER_FOLDER, exist_ok=True)  
        with open(SAVE_PATH, 'w', encoding='utf-8') as f:
            json.dump({'last_dir': folder, 'last_json_dir': json_folder}, f)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())