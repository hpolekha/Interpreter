from my_token import *
from lexer import *
from source import *

#
# Unit Tests for Lexer
#

def test_token_type(source_str, valid_token_type):
    lexer = Lexer(SourceString(source_str))

    token = lexer.get_next_token()

    # print(str(token.token_type) + " VS " + str(valid_token_type))
    assert(token.token_type == valid_token_type)

def test_token_value(source_str, valid_token_value):
    lexer = Lexer(SourceString(source_str))

    token = lexer.get_next_token()

    # print(str(token.token_value) + " VS " + str(valid_token_value))
    assert(token.token_value == valid_token_value)

def test_token(source_str, valid_token_type, valid_token_value):
    test_token_type(source_str, valid_token_type)
    test_token_value(source_str, valid_token_value)

# -- do tests -- #

test_token_type("", TokenType.T_EOF)

test_token("(", TokenType.T_LPAREN, "(")
test_token(")", TokenType.T_RPAREN, ")")
test_token("{", TokenType.T_LBRACE,"{")
test_token("}", TokenType.T_RBRACE,"}")

test_token("''", TokenType.T_TXTCONST, "")
test_token_type("'", TokenType.T_ERROR)
test_token_type('"\""', TokenType.T_TXTCONST)
test_token('"abc"', TokenType.T_TXTCONST, "abc")
test_token("'abc''def'", TokenType.T_TXTCONST, "abcdef")  

test_token("tmp", TokenType.T_IDENTIFIER, "tmp")
test_token("tmp123", TokenType.T_IDENTIFIER, "tmp123")
test_token("tmp_123", TokenType.T_IDENTIFIER, "tmp_123")
test_token("tmp_123_", TokenType.T_IDENTIFIER, "tmp_123_")
test_token_type("4tmp", TokenType.T_ERROR)
test_token_type("_tmp", TokenType.T_ERROR)
test_token("tx", TokenType.T_IDENTIFIER, "tx")
test_token_type("xt", TokenType.T_ERROR)            # identifiers can start with neither the rom nor arabic numeral

test_token("XX", TokenType.T_ROMANCONST, "XX")
test_token("L", TokenType.T_ROMANCONST, "L")
test_token("CI", TokenType.T_ROMANCONST, "CI")
test_token("m", TokenType.T_ROMANCONST, "M")
test_token("dC", TokenType.T_ROMANCONST, "DC")
test_token("viv", TokenType.T_ROMANCONST, "VIV")
test_token_type("XXA", TokenType.T_ERROR)        # Invalid syntax of rom numeral
test_token_type("XX?", TokenType.T_ERROR)          # Invalid symbol of rom numeral

test_token("+", TokenType.T_PLUS, "+")
test_token("-", TokenType.T_MINUS,"-")
test_token_type("-?", TokenType.T_ERROR)
test_token_type("+if", TokenType.T_ERROR)

test_token("*", TokenType.T_MULTIPLY, "*")
test_token("/", TokenType.T_DIVIDE, "/")
test_token_type("*+", TokenType.T_ERROR)
test_token_type("/i", TokenType.T_ERROR)

test_token(">", TokenType.T_GREATERTHAN, ">")
test_token(">=", TokenType.T_GREATEREQUAL, ">=")
test_token("<", TokenType.T_LESSTHAN, "<")
test_token("<=", TokenType.T_LESSEQUAL, "<=")
test_token("=", TokenType.T_ASSIGNMENT, "=")
test_token("==", TokenType.T_EQUAL, "==")
test_token("!", TokenType.T_UNEGATION, "!")
test_token("!=", TokenType.T_NOTEQUAL, "!=")
test_token_type("=#", TokenType.T_ERROR)
test_token_type(">=0", TokenType.T_ERROR)
test_token_type("!=a", TokenType.T_ERROR)

test_token("nil", TokenType.T_NIL, "nil")
test_token("fun", TokenType.T_FUN, "fun")
test_token("read", TokenType.T_READ, "read")
test_token("ifel", TokenType.T_IFEL, "ifel")
test_token("or", TokenType.T_OR, "or")
test_token_type("or&", TokenType.T_ERROR)
test_token("ora", TokenType.T_IDENTIFIER, "ora")

test_token("12425", TokenType.T_INTCONST, 12425)
test_token("12425.1324", TokenType.T_REALCONST, 12425.1324)
test_token_type("12425.", TokenType.T_ERROR)
test_token_type("12425a", TokenType.T_ERROR)
test_token_type("12425.13a", TokenType.T_ERROR)
test_token_type("12425#", TokenType.T_ERROR)
test_token_type("12425.$", TokenType.T_ERROR)
test_token("0.123456789012345678", TokenType.T_REALCONST, 0.123456789012345)  # To 15 numbers after .
test_token_type("2147483648", TokenType.T_ERROR)    # Out-of-range number

test_token_type("'aaa\\\\'", TokenType.T_TXTCONST)    
