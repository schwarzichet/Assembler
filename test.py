from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat
from PyQt5.QtWidgets import (QApplication, QFileDialog, QMainWindow, QMenu, QMessageBox, QTextEdit)

from instructions import R_TYPE, J_TYPE, I_TYPE, REGISTERS


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupFileMenu()

        self.setupHelpMenu()

        self.setupEditor()

        self.setCentralWidget(self.editor)

        self.setWindowTitle("Syntax Highlighter")

    def about(self):
        QMessageBox.about(self, "About Syntax Highlighter",

                          "<p>The <b>Syntax Highlighter</b> example shows how to "
                          "perform simple syntax highlighting by subclassing the "
                          "QSyntaxHighlighter class and describing highlighting "
                          "rules using regular expressions.</p>")

    def newFile(self):
        self.editor.clear()

    def openFile(self, path=None):
        f_name = QFileDialog.getOpenFileName(self, 'Open file')

        if f_name[0]:
            with open(f_name[0], 'r', encoding='utf8', errors='ignore') as f:
                data = f.read()
                self.editor.setPlainText(data)

        print(f_name)

    def setupEditor(self):
        font = QFont()

        font.setFamily('Courier')

        font.setFixedPitch(True)

        font.setPointSize(10)

        self.editor = QTextEdit()

        self.editor.setFont(font)

        self.highlighter = Highlighter(self.editor.document())

    def setupFileMenu(self):
        fileMenu = QMenu("&File", self)

        self.menuBar().addMenu(fileMenu)

        fileMenu.addAction("&New...", self.newFile, "Ctrl+N")

        fileMenu.addAction("&Open...", self.openFile, "Ctrl+O")

        fileMenu.addAction("E&xit", QApplication.instance().quit, "Ctrl+Q")

    def setupHelpMenu(self):
        helpMenu = QMenu("&Help", self)

        self.menuBar().addMenu(helpMenu)

        helpMenu.addAction("&About", self.about)

        helpMenu.addAction("About &Qt", QApplication.instance().aboutQt)


class Highlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        instruction_format = QTextCharFormat()
        instruction_format.setForeground(Qt.darkBlue)
        instruction_format.setFontWeight(QFont.Bold)
        self.instructions = list(R_TYPE.keys()) + list(I_TYPE.keys()) + list(J_TYPE.keys())
        instruction_patterns = ["\\b{}\\b".format(w) for w in self.instructions]
        self.highlightingRules = [(QRegExp(pattern), instruction_format) for pattern in instruction_patterns]

        register_format = QTextCharFormat()
        register_format.setForeground(Qt.red)
        self.registers = list(REGISTERS.keys())
        register_patterns = [w[1:] for w in self.registers]
        print(register_patterns)
        self.highlightingRules += ([(QRegExp("\\$" + pattern), register_format) for pattern in register_patterns])

        singleLineCommentFormat = QTextCharFormat()
        singleLineCommentFormat.setForeground(Qt.green)
        self.highlightingRules.append((QRegExp("//[^\n]*"), singleLineCommentFormat))

        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(Qt.green)

        self.commentStartExpression = QRegExp("/\\*")
        self.commentEndExpression = QRegExp("\\*/")

    def highlightBlock(self, text):
        for pattern, highlight_format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, highlight_format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    window = MainWindow()

    window.resize(640, 512)

    window.show()

    sys.exit(app.exec_())
