class OwnError(Exception):
    def __init__(self, msg, row, col, code):
        self.msg = msg
        self.row = row
        self.col = col
        self.code = code
        # print(self.code)

class InterpreterError(OwnError):
    def __init__(self, msg, row, col, code=None):
        super().__init__(msg, row, col, code)

    def __str__(self):
        return  "Interpreter: " + self.msg + ' - row: ' + str(self.row) + ' col: ' + str(self.col)

class ParserError(OwnError):
    def __init__(self, msg, row, col, code=None):
        super().__init__(msg, row, col, code)

    def __str__(self):
        return "Parser: " + self.msg + ' - row: ' + str(self.row) + ' col: ' + str(self.col)

class LexerError(OwnError):
    def __init__(self, msg, row, col, code=None):
        super().__init__(msg, row, col, code)

    def __str__(self):
        return "Lexer: " + self.msg + ' - row: ' + str(self.row) + ' col: ' + str(self.col)