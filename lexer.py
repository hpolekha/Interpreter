from my_token import *
from error import *
from limits import *

class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos_row = 1
        self.pos_col = 1
        self.token_pos_row = 1
        self.token_pos_col = 1
        self.cur_char = source.read_next_symbol()

    def get_next_token(self):
        
        self.skip_whitespaces()
        
        if len(self.cur_char) < 1:
            return Token(token_type=TokenType.T_EOF, token_value=self.cur_char, pos_row=self.token_pos_row, pos_col=self.token_pos_col)

        token = self.get_bracket_token()
        if token:
            return token

        token = self.get_concat_token()
        if token:
            return token

        token = self.get_integer_or_double_token()
        if token:
            return token

        token = self.get_roman_num_or_keyword_token()
        if token:
            return token
        
        token = self.get_plus_or_minus_token()
        if token:
            return token

        token = self.get_mult_or_div_token()
        if token:
            return token

        token = self.get_condition_or_assignment_token()
        if token:
            return token

        token = self.get_string_token()
        if token:
            return token

        token = self.get_keyword_or_identifier_token()
        if token:
            return token

        # error
        error_msg = 'Symbol ' + self.cur_char + ' is not supposed.'
        error = self.generate_error(error_code=ErrorCode.SYNTAX_ERROR, error_msg=error_msg)
        token = Token(token_type=TokenType.T_ERROR, token_value=self.cur_char, pos_row=self.token_pos_row, pos_col=self.token_pos_col, error=error)
        self.read_whole_incorrect_token()
        return token

    def read_whole_incorrect_token(self):
        while len(self.cur_char) > 0 and not self.is_bracket(self.cur_char) and not self.cur_char.isspace():
            self.read_next_char() 

    def get_keyword_or_identifier_token(self):
        if self.cur_char.isalpha() and not self.is_roman_digit(self.cur_char):
            tmp = ''
            counter = 0
            while self.cur_char.isalpha() or self.cur_char.isdigit() or self.cur_char == '_':
                if counter == MAX_LENGTH_OF_IDENTIFIER:
                    return self.max_length_of_identifier_reached(token_value=tmp)

                tmp += self.cur_char
                counter += 1
                self.read_next_char()
            if self.is_bracket(self.cur_char) or self.cur_char.isspace() or len(self.cur_char) < 1:
                if tmp in keyword_dict:
                    token = Token(token_type=keyword_dict[tmp], token_value=tmp, pos_row=self.token_pos_row, pos_col=self.token_pos_col)
                else:
                    token = Token(token_type=TokenType.T_IDENTIFIER, token_value=tmp, pos_row=self.token_pos_row, pos_col=self.token_pos_col)
                return token
            else:
                # error
                # a#
                error_msg = 'Symbol ' + self.cur_char + ' is not supposed.'
                error = self.generate_error(error_code=ErrorCode.BAD_IDENTIFIER_NAME, error_msg=error_msg)
                
                token_value = tmp + self.cur_char

                self.read_whole_incorrect_token()

                token = Token(token_type=TokenType.T_ERROR, token_value=token_value, pos_row=self.token_pos_row, pos_col=self.token_pos_col, error=error)
                return token
        else:
            return None

    def get_string_token(self):
        token = self.get_one_string_token()
        if token:
            if token.token_type == TokenType.T_ERROR:
                return token
            concat_value = token.token_value
            next_token = self.get_one_string_token()
            while next_token and next_token.token_type != TokenType.T_ERROR:
                concat_value += next_token.token_value
                if len(concat_value) > MAX_LENGTH_OF_STRING:
                    token.token_type = TokenType.T_ERROR
                    token.error = self.generate_error(error_code=ErrorCode.OUT_OF_RANGE, error_msg="Out-of-range txt", pos_row=self.token_pos_row, pos_col=self.token_pos_col)
                    next_token = self.get_one_string_token()
                    while next_token:
                        next_token = self.get_one_string_token()
                    return token
                next_token = self.get_one_string_token()
            if token.token_type == TokenType.T_ERROR:
                token.token_type = TokenType.T_ERROR
                return token
            token.token_value = concat_value
            return token
        else:
            return None

    def get_one_string_token(self):
        if self.cur_char == '"' or self.cur_char == "'":
            tmp = self.cur_char
            if not self.read_next_char():
                # error
                # "
                error_msg = 'Closing quote is missing.'
                error = self.generate_error(error_code=ErrorCode.NO_CLOSING_QUOT, error_msg=error_msg, pos_row=self.token_pos_row, pos_col=self.token_pos_col)
                return Token(token_type=TokenType.T_ERROR, token_value=tmp, pos_row=self.token_pos_row, pos_col=self.token_pos_col, error=error)
            literal = ""
            special_char = False
            counter = 0
            while self.cur_char != tmp or special_char:
                literal += self.cur_char
                # special_char = False
                if self.cur_char == '\\':
                    special_char = not special_char
                counter += 1
                if counter > MAX_LENGTH_OF_STRING:
                    error_msg = 'Out-of-range txt'
                    error = self.generate_error(error_code=ErrorCode.OUT_OF_RANGE, error_msg=error_msg, pos_row=self.token_pos_row, pos_col=self.token_pos_col)

                    while len(self.cur_char) > 0 and (self.cur_char != tmp or special_char):
                        # special_char = False
                        if self.cur_char == '\\':
                            special_char = not special_char
                        self.read_next_char()
                    self.read_next_char()
                    return Token(token_type=TokenType.T_ERROR, token_value=literal, pos_row=self.token_pos_row, pos_col=self.token_pos_col, error=error)

                if not self.read_next_char():
                    # error
                    # "a
                    error_msg = 'Closing quote is missing.'
                    error = self.generate_error(error_code=ErrorCode.NO_CLOSING_QUOT, error_msg=error_msg, pos_row=self.token_pos_row, pos_col=self.token_pos_col)
                    return Token(token_type=TokenType.T_ERROR, token_value=tmp, pos_row=self.token_pos_row, pos_col=self.token_pos_col, error=error)
            token = Token(token_type=TokenType.T_TXTCONST, token_value=literal, pos_row=self.token_pos_row, pos_col=self.token_pos_col)
            self.read_next_char()
            return token
        return None

    def get_condition_or_assignment_token(self):
        chars = ['<', '>', '=', '!']
        if self.cur_char in chars:
            tmp = self.cur_char
            self.read_next_char()
            if self.is_bracket(self.cur_char) or self.cur_char.isspace() or len(self.cur_char) < 1:
                token = Token(token_type=keyword_dict[tmp], token_value=tmp, pos_row=self.token_pos_row, pos_col=self.token_pos_col)
                return token
            elif self.cur_char == '=':
                self.read_next_char()
                if self.is_bracket(self.cur_char) or self.cur_char.isspace() or len(self.cur_char) < 1:
                    token = Token(token_type=keyword_dict[tmp + '='], token_value=tmp+'=', pos_row=self.token_pos_row, pos_col=self.token_pos_col)
                    return token
                else:
                    # error
                    # <=?

                    token_value = tmp + '=' + self.cur_char

                    self.read_whole_incorrect_token()

                    error_msg = 'Operator ' + token_value + ' not found'
                    error = self.generate_error(error_code=ErrorCode.OPERATOR_NOT_FOUND, error_msg=error_msg, pos_row=self.token_pos_row, pos_col=self.token_pos_col)
                    token = Token(token_type=TokenType.T_ERROR, token_value=token_value, pos_row=self.token_pos_row, pos_col=self.token_pos_col, error=error)
                    return token
                   
            else:
                # error
                # print("Error3")
                # <?
                token_value = tmp + self.cur_char

                self.read_whole_incorrect_token()

                error_msg = 'Operator ' + token_value + ' not found'
                error = self.generate_error(error_code=ErrorCode.OPERATOR_NOT_FOUND, error_msg=error_msg, pos_row=self.token_pos_row, pos_col=self.token_pos_col)
                return Token(token_type=TokenType.T_ERROR, token_value=token_value, pos_row=self.token_pos_row, pos_col=self.token_pos_col, error=error)
        else:
            return None

    def get_mult_or_div_token(self):
        if self.cur_char == '*' or self.cur_char == '/':
            tmp = self.cur_char
            self.read_next_char()
            if self.is_bracket(self.cur_char) or self.cur_char.isspace() or len(self.cur_char) < 1:
                token = Token(token_type=keyword_dict[tmp], token_value=tmp, pos_row=self.token_pos_row, pos_col=self.token_pos_col)
                return token
            else:
                # error
                # *?
                token_value = tmp + self.cur_char

                self.read_whole_incorrect_token()

                error_msg = 'Operator ' + token_value + ' not found'
                error = self.generate_error(error_code=ErrorCode.OPERATOR_NOT_FOUND, error_msg=error_msg, pos_row=self.token_pos_row, pos_col=self.token_pos_col)
                return Token(token_type=TokenType.T_ERROR, token_value=token_value, pos_row=self.token_pos_row, pos_col=self.token_pos_col, error=error)
        return None

    def get_plus_or_minus_token(self):
        if self.cur_char == '-' or self.cur_char == '+':
            tmp = self.cur_char
            self.read_next_char()
            if self.is_bracket(self.cur_char) or self.cur_char.isspace() or len(self.cur_char) < 1:
                token = Token(token_type=keyword_dict[tmp], token_value=tmp, pos_row=self.token_pos_row, pos_col=self.token_pos_col)
                return token
            else:
                return self.part_after_plus_minus_recognized(tmp)
        else:
            return None
    
    def part_after_plus_minus_recognized(self, sign):
        token = self.get_integer_or_double_token()
        if token:
            if sign == '-':
                if token.token_type == TokenType.T_ERROR:
                    token.token_value = '-' + token.token_value
                else:
                    token.token_value *= -1
            return token

        token = self.get_roman_num_or_keyword_token()
        if token:
            if token.token_type == TokenType.T_ERROR:
                return token
            if token.token_value in keyword_dict:
                # error
                # +if
                token_value = sign  + token.token_value
                return self.invalid_syntax_recognized(token_value=token_value)
            else:
                if sign == '-':
                    token.token_value = '-' + token.token_value
                return token

        # if -/+ before variable 
        token = self.get_keyword_or_identifier_token()
        if token:
            if token.token_type == TokenType.T_ERROR:
                return token
            if token.token_value in keyword_dict:
                # error
                # +loop
                token_value = sign + token.token_value
                return self.invalid_syntax_recognized(token_value=token_value)
            else:
                if sign == '-':
                    token.token_value = '-' + token.token_value
                return token        

        # error
        # +?
        token_value = sign + self.cur_char
        return self.invalid_syntax_recognized(token_value=token_value, should_read_until_end_of_token=True)


    def get_roman_num_or_keyword_token(self):
        if self.is_roman_digit(self.cur_char):
            token_value = ""
            counter = 0
            while self.is_roman_digit(self.cur_char):
                if counter == MAX_LENGTH_OF_ROMAN_NUM:
                    return self.out_of_range_reached(token_value)
                token_value += self.cur_char
                counter += 1
                self.read_next_char()
            if len(self.cur_char) > 0 and not self.is_bracket(self.cur_char) and not self.cur_char.isspace():
                return self.non_roman_digit_recognized(counter=counter, token_value=token_value)
            else:
                token = Token(token_type=TokenType.T_ROMANCONST, token_value=token_value.upper(), pos_row=self.token_pos_row, pos_col=self.token_pos_col)
                return token
        else:
            return None

    def non_roman_digit_recognized(self, counter, token_value):
        while self.cur_char.isalpha() or self.cur_char.isdigit() or self.cur_char == '_':
            if counter == MAX_LENGTH_OF_IDENTIFIER:
                return self.max_length_of_identifier_reached(token_value)
            token_value += self.cur_char
            counter += 1
            self.read_next_char()
                
        if self.is_bracket(self.cur_char) or self.cur_char.isspace() or len(self.cur_char) < 1:
            if token_value in keyword_dict:
                token = Token(token_type=keyword_dict[token_value], token_value=token_value, pos_row=self.token_pos_row, pos_col=self.token_pos_col)
                return token
            else:
                # error
                # XIVas
               return self.invalid_syntax_recognized(token_value=token_value)
        else:
            # error
            # XVIA?
            token_value = token_value + self.cur_char
            return self.invalid_syntax_recognized(token_value=token_value, should_read_until_end_of_token=True)
            
    def invalid_syntax_recognized(self, token_value, should_read_until_end_of_token=False):
        if should_read_until_end_of_token:
            self.read_whole_incorrect_token()
        error_msg = 'Invalid syntax: ' + token_value
        error = self.generate_error(error_code=ErrorCode.SYNTAX_ERROR, error_msg=error_msg, pos_row=self.token_pos_row, pos_col=self.token_pos_col)
        return Token(token_type=TokenType.T_ERROR, token_value=token_value, pos_row=self.token_pos_row, pos_col=self.token_pos_col, error=error)

    def max_length_of_identifier_reached(self, token_value):
        self.read_whole_incorrect_token()

        error_msg = 'Too long identifier'
        error = self.generate_error(error_code=ErrorCode.TOO_LONG_IDENTIFIER, error_msg=error_msg, pos_row=self.token_pos_row, pos_col=self.token_pos_col)
        token = Token(token_type=TokenType.T_ERROR, token_value=token_value, pos_row=self.token_pos_row, pos_col=self.token_pos_col, error=error)
        return token
    
    def is_roman_digit(self, ch):
         return (ch.upper() == 'I' 
                or ch.upper() == 'V'
                or ch.upper() == 'X'
                or ch.upper() == 'L'
                or ch.upper() == 'C' 
                or ch.upper() == 'D'
                or ch.upper() == 'M')

    def get_integer_or_double_token(self):
        if self.cur_char.isdigit():
            token_value = 0
            while self.cur_char.isdigit():
                token_value *= 10
                token_value += int(self.cur_char)
                if token_value > MAX_INT_ABSOLUTE_VALUE:
                    # error
                    return self.out_of_range_reached(token_value)
                self.read_next_char()
            
            if self.cur_char == '.':
                return self.dot_in_number_was_recognized(token_value)
            elif len(self.cur_char) > 0 and not self.is_bracket(self.cur_char) and not self.cur_char.isspace():
                # error
                # 123?
                token_value = str(token_value) + self.cur_char
                return self.invalid_syntax_in_number_recognizedd(token_value)
            else:
                token = Token(token_type=TokenType.T_INTCONST, token_value=token_value, pos_row=self.token_pos_row, pos_col=self.token_pos_col)
                return token
        else:
            return None

    def dot_in_number_was_recognized(self, token_value):
        self.read_next_char()
        if self.cur_char.isdigit():
            counter = 0
            tmp = 0
            while self.cur_char.isdigit():
                if counter == MAX_DOUBLE_PRECISION:
                    return self.max_double_precision_reached(token_value=token_value, after_comma_part=tmp, counter=counter)
                tmp *= 10
                tmp += int(self.cur_char)
                counter += 1
                self.read_next_char()

            if len(self.cur_char) > 0 and not self.is_bracket(self.cur_char) and not self.cur_char.isspace():
                # error
                # 123.456?
                rest = str(tmp)
                rest = str(rest)
                while len(rest) < counter:
                    rest = '0' + rest

                token_value = str(token_value) + '.' + rest + self.cur_char
                return self.invalid_syntax_in_number_recognizedd(token_value)
            else:
                tmp /= 10 ** counter
                token_value += tmp
                token = Token(token_type=TokenType.T_REALCONST, token_value=token_value, pos_row=self.token_pos_row, pos_col=self.token_pos_col)
                return token
        else:
            # error
            # 123.?
            token_value = str(token_value) + '.' + self.cur_char
            return self.invalid_syntax_in_number_recognizedd(token_value)

    def invalid_syntax_in_number_recognizedd(self, token_value):
        error_char_row = self.pos_row
        error_char_col = self.pos_col

        self.read_whole_incorrect_token()  

        error_msg =  'Invalid syntax - wrong number format: ' + token_value      
        error = self.generate_error(error_code=ErrorCode.SYNTAX_ERROR, error_msg=error_msg, pos_row=error_char_row, pos_col=error_char_col)
        return Token(token_type=TokenType.T_ERROR, token_value=token_value, pos_row=self.token_pos_row, pos_col=self.token_pos_col, error=error)

    def max_double_precision_reached(self, token_value, after_comma_part, counter):
        after_comma_part /= 10 ** counter
        token_value += after_comma_part
        token = Token(token_type=TokenType.T_REALCONST, token_value=token_value, pos_row=self.token_pos_row, pos_col=self.
        token_pos_col)
        while len(self.cur_char) > 0 and not self.is_bracket(self.cur_char) and not self.cur_char.isspace():
            if not self.cur_char.isdigit():
                error_msg =  'Invalid syntax - wrong number format: unexpected ' + self.cur_char
                error = self.generate_error(error_code=ErrorCode.SYNTAX_ERROR, error_msg=error_msg, pos_row=self.token_pos_row, pos_col=self.token_pos_col)
                self.read_whole_incorrect_token()
                return Token(token_type=TokenType.T_ERROR, token_value=token_value, pos_row=self.token_pos_row, pos_col=self.token_pos_col, error=error)
            self.read_next_char()
        return token

    def out_of_range_reached(self, token_value):
        error_msg = 'Out-of-range number'
        error = self.generate_error(error_code=ErrorCode.OUT_OF_RANGE, error_msg=error_msg, pos_row=self.token_pos_row, pos_col=self.token_pos_col)

        while len(self.cur_char) > 0 and not self.is_bracket(self.cur_char) and not self.cur_char.isspace():
            self.read_next_char()

        return Token(token_type=TokenType.T_ERROR, token_value=token_value, pos_row=self.token_pos_row, pos_col=self.token_pos_col, error=error)

    def get_bracket_token(self):
        if self.is_bracket(self.cur_char):
            token = Token(token_type=keyword_dict[self.cur_char], token_value=self.cur_char, pos_row=self.token_pos_row, pos_col=self.token_pos_col)

            self.read_next_char()
            return token
        else:
            return None

    def get_concat_token(self):
        if self.cur_char == '.':
            token = Token(token_type=keyword_dict[self.cur_char], token_value=self.cur_char, pos_row=self.token_pos_row, pos_col=self.token_pos_col)

            self.read_next_char()
            return token
        else:
            return None

    def is_bracket(self, ch):
        return (ch == '(' 
                or ch == ')'
                or ch == '{'
                or ch == '}')

    def skip_whitespaces(self):
        while len(self.cur_char) > 0 and self.cur_char.isspace():
            self.read_next_char()

        self.token_pos_row = self.pos_row
        self.token_pos_col = self.pos_col

    def read_next_char(self):
        if self.cur_char == '\n':
            self.pos_row += 1
            self.pos_col = 0
        self.cur_char = self.source.read_next_symbol()
        self.pos_col += 1

        # print(self.cur_char)

        if len(self.cur_char) < 1:
            return False
        return True

    def generate_error(self, error_code, error_msg, pos_row=-1, pos_col=-1):
        if pos_row == -1:
            pos_row = self.pos_row
        if pos_col == -1:
            pos_col = self.pos_col
        return Error(error_code=error_code, error_msg=error_msg, pos_row=pos_row, pos_col=pos_col)