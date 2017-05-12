import sys

from PyQt5.QtCore import QSize, QRect, Qt
from PyQt5.QtGui import QIcon, QFont, QPainter, QColor, QTextFormat
from PyQt5.QtWidgets import QFileDialog, QPlainTextEdit, QGridLayout, QTextEdit
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QToolTip, QMessageBox, QDesktopWidget, qApp, QAction

import syntax
from disassambly import disassambly, dis_coe
from mips_parser import assemble, to_coe


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.lineNumberArea = LineNumberArea(self)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)

    def lineNumberAreaWidth(self):
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 3 + self.fontMetrics().width('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        print('CodeEditor.updateLineNumberAreaWidth: margin = {}'.format(self.lineNumberAreaWidth()))
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        print('CodeEditor.updateLineNumberArea: rect = {}, dy = {}'.format(rect, dy))

        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(),
                                       rect.height())

        print('CodeEditor.updateLineNumberArea: rect.contains(self.viewport().rect()) = {}'.format(
            rect.contains(self.viewport().rect())))
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(),
                                              self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        print('CodeEditor.lineNumberAreaPaintEvent')

        painter.fillRect(event.rect(), QColor(0xFFFFFF))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Just to make sure I use the right font
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(block_number + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(), height,
                                 Qt.AlignCenter, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlightCurrentLine(self):
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            line_color = QColor(237, 239, 241)

            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)


class Main_Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.assemble_area = CodeEditor()
        self.bin_area = CodeEditor()
        self.highlighter_1 = syntax.MipsHighlighter(self.assemble_area.document())
        self.highlighter_2 = syntax.BinHighlighter(self.bin_area.document())
        self.set_font()
        self.set_ui()

    def set_ui(self):
        grid = QGridLayout()
        self.setLayout(grid)

        grid.addWidget(self.assemble_area, 1, 0)
        grid.addWidget(self.bin_area, 1, 1)

    def set_font(self):
        font = QFont()
        font.setFamily('Consolas')
        font.setFixedPitch(True)
        font.setPointSize(12)
        self.assemble_area.setFont(font)
        self.bin_area.setFont(font)


class IDE(QMainWindow):
    def __init__(self):
        super().__init__()

        self.main_widget = Main_Widget()
        self.init_ui()
        self.now_asm_file_address = None
        self.now_bin_file_address = None

    def make_menu(self):
        new_file = QAction('&New', self)
        new_file.setShortcut('Ctrl+N')
        new_file.setStatusTip('New File')
        new_file.triggered.connect(self.new_file_action)

        open_file_action = QAction('&Open', self)
        open_file_action.setShortcut('Ctrl+O')
        open_file_action.setStatusTip('Open assemble File')
        open_file_action.triggered.connect(self.open_file)

        open_bin_file_action = QAction('&Open bin/coe file', self)
        open_bin_file_action.setShortcut('Ctrl+Alt+O')
        open_bin_file_action.setStatusTip('Open bin/coe file')
        open_bin_file_action.triggered.connect(self.open_bin_file)

        save_file_action = QAction('&Save', self)
        save_file_action.setShortcut('Ctrl+S')
        save_file_action.setStatusTip('Save File')
        save_file_action.triggered.connect(self.save_file)

        save_bin_file_action = QAction('&Save bin file', self)
        save_bin_file_action.setShortcut('Ctrl+Alt+S')
        save_bin_file_action.setStatusTip('Save bin File')
        save_bin_file_action.triggered.connect(self.save_bin_file)

        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(qApp.quit)

        assemble_file_action = QAction('&Assemble', self)
        assemble_file_action.setShortcut('F9')
        assemble_file_action.setStatusTip('Assemble')
        assemble_file_action.triggered.connect(self.assemble_file)

        assemble_to_coe_action = QAction('&Assemble to Coe', self)
        assemble_to_coe_action.setShortcut('F11')
        assemble_to_coe_action.setStatusTip('Assemble to Coe')
        assemble_to_coe_action.triggered.connect(self.assemble_to_coe)

        disassemble_file_action = QAction('&Disassemble', self)
        disassemble_file_action.setShortcut('F10')
        disassemble_file_action.setStatusTip('Disassemble')
        disassemble_file_action.triggered.connect(self.disassemble_file)

        disassemble_coe_action = QAction('Disassemble coe', self)
        disassemble_coe_action.setShortcut('F12')
        disassemble_coe_action.setStatusTip('Disassemble coe')
        disassemble_coe_action.triggered.connect(self.disassemble_coe)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        for i in (new_file, open_file_action, open_bin_file_action, save_file_action, exit_action):
            file_menu.addAction(i)

        build_menu = menu_bar.addMenu('&Build')
        for i in (assemble_file_action, disassemble_file_action, assemble_to_coe_action, disassemble_coe_action):
            build_menu.addAction(i)

    def init_ui(self):
        self.make_menu()
        self.setCentralWidget(self.main_widget)
        self.resize(1200, 800)
        self.center()
        QToolTip.setFont(QFont('SansSerif', 10))

        self.statusBar().showMessage('Ready')

        self.setWindowTitle('MIPSAssembler')
        self.setWindowIcon(QIcon('icon.ico'))

        self.show()

    def new_file_action(self):
        self.main_widget.assemble_area.clear()
        self.main_widget.bin_area.clear()

    def open_file(self):
        f_name = QFileDialog.getOpenFileName(self, 'Open file', '', 'Assemble files (*.asm *.s);;All files(*)')
        if f_name[0]:
            with open(f_name[0], 'r', encoding='utf8', errors='ignore') as f:
                data = f.read()
                self.main_widget.assemble_area.setPlainText(data)

        self.statusBar().showMessage('open file {}'.format(f_name[0]))
        self.now_asm_file_address = f_name

        print(f_name)

    def open_bin_file(self):
        f_name = QFileDialog.getOpenFileName(self, 'Open file', '', 'bin files (*.coe *.bin);;All files(*)')
        if f_name[0]:
            with open(f_name[0], 'r', encoding='utf8', errors='ignore') as f:
                data = f.read()
                self.main_widget.bin_area.setPlainText(data)

        self.statusBar().showMessage('open file {}'.format(f_name[0]))
        self.now_bin_file_address = f_name

        print(f_name)

    def save_file(self):

        if self.now_asm_file_address is None:
            self.now_asm_file_address = QFileDialog.getSaveFileName(self, 'Save file')
        if self.now_asm_file_address[0]:
            with open(self.now_asm_file_address[0], 'w', encoding='utf8', errors='ignore') as f:
                f.write(self.main_widget.assemble_area.toPlainText())
                print(self.now_asm_file_address)
        # self.now_asm_file_address = f_name
        self.statusBar().showMessage('save file {}'.format(self.now_asm_file_address[0]))

    def save_bin_file(self):
        if self.now_bin_file_address is None:
            self.now_bin_file_address = QFileDialog.getSaveFileName(self, 'Save file')
            # print(self.now_bin_file_address)
        if self.now_bin_file_address[0]:
            with open(self.now_bin_file_address[0], 'w', encoding='utf8', errors='ignore') as f:
                f.write(self.main_widget.bin_area.toPlainText())
        # self.now_bin_file_address = f_name
        self.statusBar().showMessage('save file {}'.format(self.now_bin_file_address[0]))

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def assemble_file(self):
        self.save_file()
        try:
            content = '\n'.join(assemble(self.now_asm_file_address[0]))
            # print(content)
        except:
            self.statusBar().showMessage('assemble fail'.format(self.now_asm_file_address))
        else:
            self.main_widget.bin_area.setPlainText(content)
            self.statusBar().showMessage('assemble file {}'.format(self.now_asm_file_address))

    def assemble_to_coe(self):
        self.save_file()
        try:
            content = '\n'.join(to_coe(self.now_asm_file_address[0]))
            self.main_widget.bin_area.setPlainText(content)
            self.statusBar().showMessage('assemble file {} to coe'.format(self.now_asm_file_address))
        except:
            self.statusBar().showMessage('assemble fail'.format(self.now_asm_file_address))

    def disassemble_file(self):
        try:

            self.save_bin_file()
            content = '\n'.join(disassambly(self.now_bin_file_address[0]))
            self.main_widget.assemble_area.setPlainText(content)
        except:
            self.statusBar().showMessage('disassemble fail'.format(self.now_asm_file_address))

    def disassemble_coe(self):
        try:
            self.save_bin_file()
            content = '\n'.join(dis_coe(self.now_bin_file_address[0]))
            self.main_widget.assemble_area.setPlainText(content)
        except:
            self.statusBar().showMessage('disassemble fail'.format(self.now_asm_file_address))

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)

    ex = IDE()

    sys.exit(app.exec_())
