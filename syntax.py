from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor

from instructions import R_TYPE, J_TYPE, I_TYPE, REGISTERS


class MipsHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        instruction_format = QTextCharFormat()
        instruction_format.setForeground(QColor(36, 147, 110))
        instruction_format.setFontWeight(QFont.Bold)
        self.instructions = list(R_TYPE.keys()) + list(I_TYPE.keys()) + list(J_TYPE.keys())
        instruction_patterns = ["\\b{}\\b".format(w) for w in self.instructions]
        self.highlightingRules = [(QRegExp(pattern), instruction_format) for pattern in instruction_patterns]

        number_format = QTextCharFormat()
        number_format.setForeground(QColor(0xD0104C))
        self.highlightingRules.append((QRegExp("\\b0[Xx][0-9A-Fa-f]+\\b|-*\\b[\d]+\\b"), number_format))

        register_format = QTextCharFormat()
        register_format.setForeground(QColor(0x0089A7))
        self.registers = list(REGISTERS.keys())
        register_patterns = [w[1:] for w in self.registers]
        print(register_patterns)
        self.highlightingRules += ([(QRegExp("\\$" + pattern), register_format) for pattern in register_patterns])

        single_line_comment_format = QTextCharFormat()
        single_line_comment_format.setForeground(QColor(0x577C8A))
        self.highlightingRules.append((QRegExp("//[^\n]*"), single_line_comment_format))

    def highlightBlock(self, text):
        for pattern, highlight_format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, highlight_format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)


class BinHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        number_format = QTextCharFormat()
        number_format.setForeground(QColor(0xD0104C))
        self.highlightingRules = [(QRegExp("\\b[0-9A-Fa-f]+\\b"), number_format)]

    def highlightBlock(self, text):
        for pattern, highlight_format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, highlight_format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)
