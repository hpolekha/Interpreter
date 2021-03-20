from enum import Enum

class ErrorCode(Enum):
    BAD_IDENTIFIER_NAME = 1
    NO_CLOSING_QUOT = 2
    OPERATOR_NOT_FOUND = 3
    SYNTAX_ERROR = 4
    OUT_OF_RANGE = 5
    TOO_LONG_IDENTIFIER = 6

class Error:
    def  __init__(self, error_code = -1, error_msg = None, pos_col = -1, pos_row = -1):
        self.error_code = error_code
        self.error_msg = error_msg  
        self.pos_col = pos_col
        self.pos_row = pos_row