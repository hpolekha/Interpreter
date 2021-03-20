from enum import Enum

class TokenType(Enum):
    T_ERROR = 1
    T_EOF = 2
    T_LPAREN = 3
    T_RPAREN = 4
    T_LBRACE = 5
    T_RBRACE = 6
    T_INTCONST = 7
    T_REALCONST = 8
    T_ROMANCONST = 9
    T_MINUS = 10
    T_PLUS = 11
    T_MULTIPLY = 12
    T_DIVIDE = 13
    T_LESSTHAN = 14
    T_GREATERTHAN = 15
    T_ASSIGNMENT = 16
    T_UNEGATION = 17
    T_LESSEQUAL = 18
    T_GREATEREQUAL = 19
    T_EQUAL = 20
    T_NOTEQUAL = 21
    T_IDENTIFIER = 22

    T_FUN = 23
    T_READ = 24
    T_WRITE = 25
    T_INT = 26
    T_REAL = 27
    T_ROM = 28
    T_TXT = 29
    T_IF = 30
    T_IFEL = 31
    T_LOOP = 32
    T_NIL = 33
    T_OR = 34
    T_AND = 35
    T_RET = 36

    T_TXTCONST = 37
    T_CONCAT = 38

    def  __str__(self):
        return self.name

keyword_dict = {
    '(': TokenType.T_LPAREN,
    ')': TokenType.T_RPAREN,
    '{': TokenType.T_LBRACE,
    '}': TokenType.T_RBRACE,
    '.': TokenType.T_CONCAT,
    '+': TokenType.T_PLUS,
    '-': TokenType.T_MINUS,
    '*': TokenType.T_MULTIPLY,
    '/': TokenType.T_DIVIDE,
    '<': TokenType.T_LESSTHAN,
    '>': TokenType.T_GREATERTHAN,
    '=': TokenType.T_ASSIGNMENT,
    '!': TokenType.T_UNEGATION,
    '<=': TokenType.T_LESSEQUAL,
    '>=': TokenType.T_GREATEREQUAL,
    '==': TokenType.T_EQUAL,
    '!=': TokenType.T_NOTEQUAL,

    'fun': TokenType.T_FUN,
    'read': TokenType.T_READ,
    'write': TokenType.T_WRITE,
    'int': TokenType.T_INT,
    'real': TokenType.T_REAL,
    'rom': TokenType.T_ROM,
    'txt': TokenType.T_TXT,
    'if': TokenType.T_IF,
    'ifel': TokenType.T_IFEL,
    'loop': TokenType.T_LOOP,
    'nil': TokenType.T_NIL,
    'or': TokenType.T_OR,
    'and': TokenType.T_AND,
    'ret': TokenType.T_RET
}

class Token:
    def __init__(self, token_type, token_value, pos_row, pos_col, error=None):
        self.token_type = token_type
        self.token_value = token_value
        self.pos_row = pos_row
        self.pos_col = pos_col
        self.error = error
    
    def get_info(self):
        return (str(self.token_type) + ' ' + str(self.token_value) + ' '
                + 'row: ' + str(self.pos_row) + ' col: ' + str(self.pos_col))
        
    def get_type(self):
        return self.token_type

    def get_value(self):
        return self.token_value
