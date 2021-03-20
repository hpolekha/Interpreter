import re
from lexer import *
from program import *
from my_token import *
from statement import *
from elements import *

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.next_token()
        # save current statemnt start position for building statement objects
        self.cur_statement_start_pos_row = -1
        self.cur_statement_start_pos_col = -1
        
    def parse_program(self):
        statements = []
        try:
            # get next statement
            statement = self.get_statement()
            while statement:
                # write into statement its start row and col position
                statement.start_pos_row = self.cur_statement_start_pos_row
                statement.start_pos_col = self.cur_statement_start_pos_col
                # save statement
                statements.append(statement)
                # get next statement
                statement = self.get_statement()
        except OwnError as ex:
            raise ex
        return Program(statements)

    def get_statement(self):
        # if end of source was reached retrun
        if self.token_type_is(TokenType.T_EOF):
            return None

        # save current statemnt start position for building statement object
        self.cur_statement_start_pos_row = self.token.pos_row
        self.cur_statement_start_pos_col = self.token.pos_col

        # each statement starts with TokenType.T_LPAREN
        # raise error otherwise
        if not self.token_type_is(TokenType.T_LPAREN):
            self.raise_parse_error(msg="There is no open left paren at the statement begining")

        self.next_token()

        # try to parse fun def statement
        statement  = self.get_fun_def_statement()
        if statement:
            return statement

        # try to parse non fun def statement
        statement  = self.get_no_fun_def_statement()
        if statement:
            return statement

        # if it is not fun def statement and not non fin def statement, raise error
        self.raise_parse_error(msg="undefined statement")

    def get_no_fun_def_statement(self, include_return_statement=False):

        # try to parse var assignment statement
        statement = self.get_var_assignment_statement()
        if statement:
            return statement

        # try to parse var create statement
        statement = self.get_var_create_statement()
        if statement:
            return statement

        # try to parse input/output statement
        statement = self.get_communicate_statement()
        if statement:
            return statement
      
        # try to parse arithmetic statement
        statement = self.get_arithmetic_statement()
        if statement:
            return statement
        
        # try to parse if/ifelse statement
        statement = self.get_conditional_statement(include_return_statement)
        if statement:
            return statement

        # try to parse loop statement
        statement = self.get_repeat_statement(include_return_statement)
        if statement:
            return statement

        # try to parse fun call statement
        statement = self.get_fun_call_statement()
        if statement:
            return statement   

        # try to parse concat statement
        statement = self.get_concat_statement()
        if statement:
            return statement 

        # try to parse condition statement
        # (< 1 2)
        statement = self.get_condition_statement()
        if statement:
            return statement

        # try to parse return statement
        statement = self.get_return_statement()  
        if statement:
            # if return statement was detected but it is outside of fun block erase error
            if include_return_statement:
                return statement
            else:
                self.raise_parse_error(msg="return statement is not allowed here")

        # if fun def statement was detected but it is inside of block erase error
        statement = self.get_fun_def_statement()  
        if statement:
                self.raise_parse_error(msg="fun def statement is not allowed here")

        return None

    def get_condition_statement(self):
        # < > <= >= == !=
        if self.token_type_is_binary_compare_operator():
            comp_operator = self.token
            self.next_token()
            # try to get first condition arg
            first_condition_arg = self.get_condition_arg()
            # try to get second condition arg
            second_condition_arg = self.get_condition_arg()
            # statement shoud ended with TokenType.T_RPAREN, otherwise raise error
            if self.token_type_is(TokenType.T_RPAREN):
                self.next_token()
                return ConditionStatement(condition=BinaryComparison(comp_operator=comp_operator.get_value(), first_condition_arg=first_condition_arg, second_condition_arg=second_condition_arg))
            else:
                self.raise_parse_error(msg="there is no closing paren in condition statement")
           
        # !
        elif self.token_type_is_unary_compare_operator():
            comp_operator = self.token
            self.next_token()
            # try to get first condition arg
            first_condition_arg = self.get_condition_arg()
            # statement shoud ended with TokenType.T_RPAREN, otherwise raise error
            if self.token_type_is(TokenType.T_RPAREN):
                self.next_token()
                return ConditionStatement(condition=UnaryComparison(comp_operator=comp_operator.get_value(), condition_arg=first_condition_arg))
            else:
                self.raise_parse_error(msg="there is no closing paren in condition statement")

        # or end
        elif self.token_type_is(TokenType.T_OR) or self.token_type_is(TokenType.T_AND):
            log_operator = self.token
            self.next_token()
            # try to get first condition arg
            first_condition_arg = self.get_condition_arg()
            # try to get second condition arg
            second_condition_arg = self.get_condition_arg()
            # statement shoud ended with TokenType.T_RPAREN, otherwise raise error
            if self.token_type_is(TokenType.T_RPAREN):
                self.next_token()
                return ConditionStatement(condition=LogComparison(log_operator=log_operator.get_value(), first_condition_arg=first_condition_arg, second_condition_arg=second_condition_arg))
            else:
                self.raise_parse_error(msg="there is no closing paren in condition statement")
            
        else:
            return None

    def get_concat_statement(self):
        # .
        if self.token_type_is(TokenType.T_CONCAT):
            self.next_token()
            # try to get first concat arg
            first_concat_arg = self.get_concat_arg()
            # try to get second concat arg
            second_concat_arg = self.get_concat_arg()
            # statement shoud ended with TokenType.T_RPAREN, otherwise raise error
            if self.token_type_is(TokenType.T_RPAREN):
                self.next_token()
                return ConcatStatement(first_concat_arg=first_concat_arg, second_concat_arg=second_concat_arg)
            else:
                self.raise_parse_error(msg="there is no closing paren in concat statement")
        else:
            return None
    
    def get_concat_arg(self):
        # (
        # concat arg as another statement
        if self.token_type_is(TokenType.T_LPAREN):
            self.next_token()
            # as fun call statement
            statement = self.get_fun_call_statement()
            if statement:
            # as concat statement
                return ConcatArg(concat_arg=statement)
            statement = self.get_concat_statement()
            if statement:
                return ConcatArg(concat_arg=statement)
            self.raise_parse_error(msg="invalid concat arg format")
        # as identifier or textconst
        elif (
            self.token_type_is(TokenType.T_TXTCONST) or
            self.token_type_is(TokenType.T_IDENTIFIER)
        ):
            value = self.token
            self.next_token()
            # build proper objects
            if value.get_type() == TokenType.T_TXTCONST:
                return ConcatArg(concat_arg=TextLiteral(value=value.get_value()))
            else:
                return ConcatArg(concat_arg=Identifier(value=value.get_value()))
        else:
            self.raise_parse_error(msg="invalid concat arg format")

    def get_fun_def_statement(self):
        # fun def keyword
        if self.token_type_is(TokenType.T_FUN):
            self.next_token()
            # next should be identifier
            if self.token_type_is(TokenType.T_IDENTIFIER):
                fun_identifier = self.token
                self.next_token()
                # next return type
                if self.token_type_is_datatype() or self.token_type_is(TokenType.T_NIL):
                    return_type = self.token.get_type()
                    self.next_token()
                    args = []
                    # next args
                    while not self.token_type_is(TokenType.T_LBRACE):
                        args.append(self.get_arg_for_fun_def())
                    # next fun block
                    fun_block = self.get_fun_block(return_type)
                    # should end with TokenType.T_RPAREN
                    if self.token_type_is(TokenType.T_RPAREN):
                        self.next_token()
                        return FunDefStatement(fun_identifier=fun_identifier.get_value(), return_type=return_type, args=args, fun_block=fun_block)
                    else:
                        self.raise_parse_error(msg="there is no closing paren in fun def statement")
                else:
                    self.raise_parse_error(msg="wrong return data type in fun def")
            else:
                self.raise_parse_error(msg="invalid fun name")
        else:
            return None

    def get_fun_block(self, return_type):
        # start with {
        if self.token_type_is(TokenType.T_LBRACE):
            self.next_token()
            statements = []
            # next read statements from block
            while not self.token_type_is(TokenType.T_RBRACE):
                if self.token_type_is(TokenType.T_LPAREN):
                    self.next_token()
                    statement = self.get_no_fun_def_statement(include_return_statement=True)
                    if statement:
                        # save it for object building
                        statements.append(statement)
                    else:
                        self.raise_parse_error(msg="invalid statement in fun block")
                else:
                    print(self.token.get_type())
                    self.raise_parse_error(msg="there is no open left paren at the statement begining")
            # should be return statement in return type is not void
            return_statement = next((el for el in statements if isinstance(el, ReturnStatement)), None)
            if not return_statement and return_type != TokenType.T_NIL:
                self.raise_parse_error(msg="there is no return statement in non-nil-return fun def")
            self.next_token()
            return FunBlock(statements=statements)
        else:
            self.raise_parse_error(msg="there is no open brace in fun block")

    def get_return_statement(self):
        # start with right keyword
        if self.token_type_is(TokenType.T_RET):
            self.next_token()
            # can return identifier literal void
            if (
                self.token_type_is(TokenType.T_IDENTIFIER)  or
                self.token_type_is_literal()  or
                self.token_type_is(TokenType.T_NIL) 
            ):
                return_token = self.token
                self.next_token()
                if self.token_type_is(TokenType.T_RPAREN):
                    self.next_token()
                    # build proper objects
                    if return_token.get_type() == TokenType.T_IDENTIFIER:
                        return ReturnStatement(return_arg=self.build_identifier_obj(return_token))
                    elif return_token.get_type() == TokenType.T_NIL:
                        return ReturnStatement(return_arg=self.build_void_obj(return_token))
                    else:
                        return ReturnStatement(return_arg=self.build_literal_obj(return_token))
                else:
                    self.raise_parse_error(msg="there is no closing paren in return statement")
            # return another statement
            elif self.token_type_is(TokenType.T_LPAREN):
                self.next_token()
                # return fun call
                statement = self.get_fun_call_statement()
                if statement:
                    if self.token_type_is(TokenType.T_RPAREN):
                        self.next_token()
                        return ReturnStatement(return_arg=statement)
                    else:
                        self.raise_parse_error(msg="there is no closing paren in return statement")
                # return arithmetic
                statement = self.get_arithmetic_statement()
                if statement:
                    if self.token_type_is(TokenType.T_RPAREN):
                        self.next_token()
                        return ReturnStatement(return_arg=statement)
                    else:
                        self.raise_parse_error(msg="there is no closing paren in return statement")
                # return concat
                statement = self.get_concat_statement()
                if statement:
                    if self.token_type_is(TokenType.T_RPAREN):
                        self.next_token()
                        return ReturnStatement(return_arg=statement)
                    else:
                        self.raise_parse_error(msg="there is no closing paren in return statement")
                # return condition
                statement = self.get_condition_statement()
                if statement:
                    if self.token_type_is(TokenType.T_RPAREN):
                        self.next_token()
                        return ReturnStatement(return_arg=statement)
                    else:
                        self.raise_parse_error(msg="there is no closing paren in return statement")
                self.raise_parse_error(msg="Invalid return value") 
            else:
                self.raise_parse_error(msg="Invalid return value") 
        else:
            return None

    def get_arg_for_fun_def(self):
        # start with (
        if self.token_type_is(TokenType.T_LPAREN):
            self.next_token()
            # next datatype
            if self.token_type_is_datatype():
                var_type = self.token
                self.next_token()
                # next identifier
                if self.token_type_is(TokenType.T_IDENTIFIER):
                    var_identifier = self.token
                    self.next_token()
                    # end with )
                    if self.token_type_is(TokenType.T_RPAREN):
                        self.next_token()
                        return FunDefArg(var_type=keyword_dict[var_type.get_value()], var_identifier=var_identifier.get_value())
                    else:
                        self.raise_parse_error(msg="there is no closing paren after arg in fun def")
                else:
                    self.raise_parse_error(msg="invalid arg name in fun def")
            else:
                self.raise_parse_error(msg="invalid arg data type in fun def")

        else:
            self.raise_parse_error(msg="there is no opening paren before arg in fun def")

    def get_repeat_statement(self, include_return_statement):
        # start with right keyword
        if self.token_type_is(TokenType.T_LOOP):
            self.next_token()
            # next (
            if self.token_type_is(TokenType.T_LPAREN):
                self.next_token()
                # next condition
                condition = self.get_condition()
                # next )
                if self.token_type_is(TokenType.T_RPAREN): 
                    self.next_token()
                    # next block
                    block = self.get_block(include_return_statement)
                    # should end with )
                    if self.token_type_is(TokenType.T_RPAREN):
                        self.next_token()
                        return RepeatStatement(condition=condition, block=block)
                    else:
                        self.raise_parse_error(msg="there is no closing paren in loop statement") 
                else:
                    self.raise_parse_error(msg="there is no right paren in loop statement after condition")
            else:
                self.raise_parse_error(msg="there is no left paren in loop statement before condition")
        else:
            return None

    def get_conditional_statement(self, include_return_statement):
        # try to prase if statement
        statement = self.get_if_statement(include_return_statement)
        if statement:
            return statement
        # try to parse if else statement    
        statement = self.get_ifelse_statement(include_return_statement)
        if statement:
            return statement
        return None

    def get_ifelse_statement(self, include_return_statement):
        # start with right keyword
        if self.token_type_is(TokenType.T_IFEL):
            self.next_token()
            # next (
            if self.token_type_is(TokenType.T_LPAREN):
                self.next_token()
                # next condition
                condition = self.get_condition()
                if self.token_type_is(TokenType.T_RPAREN): 
                    # next )
                    self.next_token()
                    # next first block 
                    firstBlock = self.get_block(include_return_statement)
                    # next second block
                    secondBlock = self.get_block(include_return_statement)
                    # should end with )
                    if self.token_type_is(TokenType.T_RPAREN):
                        self.next_token()
                        return IfElseStatement(condition=condition, block_true=firstBlock, block_false=secondBlock)
                    else:
                        self.raise_parse_error(msg="there is no closing paren in ifelse statement") 
                else:
                    self.raise_parse_error(msg="there is no right paren in if else statement after condition")
            else:
                self.raise_parse_error(msg="there is no left paren in if else statement before condition")
        else:
            return None

    def get_if_statement(self, include_return_statement):
        # start with right keyword
        if self.token_type_is(TokenType.T_IF):
            self.next_token()
            # next (
            if self.token_type_is(TokenType.T_LPAREN):
                self.next_token()
                # next condition
                condition = self.get_condition()
                # next )
                if self.token_type_is(TokenType.T_RPAREN): 
                    self.next_token()
                    # next block
                    block = self.get_block(include_return_statement)
                    # should end with )
                    if self.token_type_is(TokenType.T_RPAREN):
                        self.next_token()
                        return IfStatement(condition=condition, block=block)
                    else:
                        self.raise_parse_error(msg="there is no closing paren in if statement")       
                else:
                    self.raise_parse_error(msg="there is no right paren in if statement after condition")
            else:
                self.raise_parse_error(msg="there is no left paren in if statement before condition")
        else:
            return None

    def get_condition(self):
        # condition as statement
        if self.token_type_is(TokenType.T_LPAREN):
            self.next_token()
            # as fun call
            statement = self.get_fun_call_statement()
            if statement:
                return Condition(condition=statement)
            # as arithmetic
            statement = self.get_arithmetic_statement()
            if statement:
                return Condition(condition=statement)
            # as condition
            statement = self.get_condition_statement()
            if statement:
                return Condition(condition=statement)
            self.raise_parse_error(msg="invalid condition")
        # condition as identifier
        elif self.token_type_is(TokenType.T_IDENTIFIER):
            condition = self.token
            self.next_token()
            return Condition(condition=self.build_identifier_obj(condition))
        # condition as literal
        elif self.token_type_is_literal():
            condition = self.token
            self.next_token()
            return Condition(condition=self.build_literal_obj(condition))
        # condition as binary compare ex. (< 1 2)
        elif self.token_type_is_binary_compare_operator():
            comp_operator = self.token
            self.next_token()
            first_condition_arg = self.get_condition_arg()
            second_condition_arg = self.get_condition_arg()
            return Condition(condition=BinaryComparison(comp_operator=comp_operator.get_value(), first_condition_arg=first_condition_arg, second_condition_arg=second_condition_arg))
        # condition as unary compare ex. (! 1)
        elif self.token_type_is_unary_compare_operator():
            comp_operator = self.token
            self.next_token()
            first_condition_arg = self.get_condition_arg()
            return Condition(condition=UnaryComparison(comp_operator=comp_operator.get_value(), condition_arg=first_condition_arg))
        # or and and ex. or arg1 arg2
        elif self.token_type_is(TokenType.T_OR) or self.token_type_is(TokenType.T_AND):
            log_operator = self.token
            self.next_token()
            first_condition_arg = self.get_condition_arg()
            second_condition_arg = self.get_condition_arg()
            return Condition(condition=LogComparison(log_operator=log_operator.get_value(), first_condition_arg=first_condition_arg, second_condition_arg=second_condition_arg))
        else:
            self.raise_parse_error(msg="unknown condition format")

    def get_condition_arg(self):
        # condition arg as another statement
        if self.token_type_is(TokenType.T_LPAREN):
            self.next_token()
            # as fun call
            statement = self.get_fun_call_statement()
            if statement:
                return ConditionArg(condition_arg=statement)
            # as arithmetic
            statement = self.get_arithmetic_statement()
            if statement:
                return ConditionArg(condition_arg=statement)
            # as condition
            statement = self.get_condition_statement()
            if statement:
                return ConditionArg(condition_arg=statement)
            self.raise_parse_error(msg="invalid condition arg format")
        # as literal
        elif self.token_type_is_literal():
            value = self.token
            self.next_token()
            return ConditionArg(condition_arg=self.build_literal_obj(value))
        # as identifier
        elif self.token_type_is(TokenType.T_IDENTIFIER):
            value = self.token
            self.next_token()
            return ConditionArg(condition_arg=self.build_identifier_obj(value))
        else:
            self.raise_parse_error(msg="invalid condition arg format")

    def token_type_is_number(self):
        # if self.token_type_is(TokenType.T_ROMANCONST):
            # return self.is_correct_roman_number()
        return (
            self.token_type_is(TokenType.T_INTCONST) or
            self.token_type_is(TokenType.T_REALCONST) or
            self.token_type_is(TokenType.T_ROMANCONST)
        )
 
    # def is_correct_roman_number(self):
    #     num_string = self.token.get_value()
    #     return re.search(r"^(-)?M{0,9}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", num_string)
        

    def token_type_is_datatype(self):
        return (
            self.token_type_is(TokenType.T_INT) or
            self.token_type_is(TokenType.T_REAL) or 
            self.token_type_is(TokenType.T_ROM) or
            self.token_type_is(TokenType.T_TXT)
        )

    def token_type_is_literal(self):
        return (
            self.token_type_is_number() or
            self.token_type_is(TokenType.T_TXTCONST)
        )

    def token_type_is_binary_compare_operator(self):
        return (
            self.token_type_is(TokenType.T_LESSTHAN) or
            self.token_type_is(TokenType.T_GREATERTHAN) or
            self.token_type_is(TokenType.T_LESSEQUAL) or
            self.token_type_is(TokenType.T_GREATEREQUAL) or
            self.token_type_is(TokenType.T_EQUAL) or
            self.token_type_is(TokenType.T_NOTEQUAL)
        )

    def token_type_is_unary_compare_operator(self):
        return self.token_type_is(TokenType.T_UNEGATION)

    def get_block(self, include_return_statement):
        # start with {
        if self.token_type_is(TokenType.T_LBRACE):
            self.next_token()
            # next try to parse statements untill } symbol
            statements = []
            while(not self.token_type_is(TokenType.T_RBRACE)):
                if self.token_type_is(TokenType.T_LPAREN):
                    self.next_token()
                    statement = self.get_no_fun_def_statement(include_return_statement)
                    # save statement for object building
                    if statement:
                        statements.append(statement)
                    else:
                        self.raise_parse_error(msg="invalid statement in block")
                else:
                    self.raise_parse_error(msg="there is no open left paren at the statement begining")
            self.next_token()
            return Block(statements=statements)
        else:
            self.raise_parse_error(msg="there is no open brace in block")

    def get_output_statement(self):
        # start with proper keyword
        if self.token_type_is(TokenType.T_WRITE):
            # next output value
            self.next_token()
            # as identifier ot literal
            if (self.token_type_is(TokenType.T_IDENTIFIER)
               or self.token_type_is_literal()):
                output_arg = self.token
                self.next_token()
                if self.token_type_is(TokenType.T_RPAREN):
                    self.next_token()
                    # build proper objects
                    if output_arg.get_type() == TokenType.T_IDENTIFIER:
                        return OutputStatement(output_arg=self.build_identifier_obj(output_arg))
                    else:
                        return OutputStatement(output_arg=self.build_literal_obj(output_arg))
                else: 
                    self.raise_parse_error(msg="there is no closing paren in the end of output statement")
            # as another statement
            elif self.token_type_is(TokenType.T_LPAREN):
                    self.next_token()
                    # as fun call
                    statement = self.get_fun_call_statement()
                    if statement:
                        if self.token_type_is(TokenType.T_RPAREN):
                            self.next_token()
                            return OutputStatement(output_arg=statement)
                        else:
                            self.raise_parse_error(msg="there is no closing paren in the end of output statement")
                    # as arithmetic
                    statement = self.get_arithmetic_statement()
                    if statement:
                        if self.token_type_is(TokenType.T_RPAREN):
                            self.next_token()
                            return OutputStatement(output_arg=statement)
                        else:
                            self.raise_parse_error(msg="there is no closing paren in the end of output statement")
                    # as concat
                    statement = self.get_concat_statement()
                    if statement:
                        if self.token_type_is(TokenType.T_RPAREN):
                            self.next_token()
                            return OutputStatement(output_arg=statement)
                        else:
                            self.raise_parse_error(msg="there is no closing paren in the end of output statement")
                    # as condition
                    statement = self.get_condition_statement()
                    if statement:
                        if self.token_type_is(TokenType.T_RPAREN):
                            self.next_token()
                            return OutputStatement(output_arg=statement)
                        else:
                            self.raise_parse_error(msg="there is no closing paren in the end of output statement")
                    self.raise_parse_error(msg="invalid arg in output statement")
            else:
                self.raise_parse_error(msg="invalid arg in output statement")
        else: 
            return None

    def build_identifier_obj(self, token):
        if token.get_type() == TokenType.T_IDENTIFIER:
            return Identifier(value=token.get_value())
        return None

    def build_number_obj(self, token):
        if token.get_type() == TokenType.T_INTCONST:
            return IntLiteral(value=token.get_value())
        elif token.get_type() == TokenType.T_REALCONST:
            return RealLiteral(value=token.get_value())
        elif token.get_type() == TokenType.T_ROMANCONST:
            try:
                return RomanLiteral(value=token.get_value())
            except:
                self.raise_parse_error(msg="Invalid rom number")
        return None

    def build_literal_obj(self, token):
        if token.get_type() == TokenType.T_TXTCONST:
            return TextLiteral(value=token.get_value())
        
        return self.build_number_obj(token)
    
    def build_void_obj(self, token):
        if token.get_type() == TokenType.T_NIL:
            return Void(value=None)
        return None
    
    def get_input_statement(self):
        # start with proper keyword
        if self.token_type_is(TokenType.T_READ):
            self.next_token()
            # next identifier of var where to read
            if self.token_type_is(TokenType.T_IDENTIFIER):
                input_arg = self.token
                self.next_token()
                # should end with )
                if self.token_type_is(TokenType.T_RPAREN):
                    self.next_token()
                    return InputStatement(input_arg=input_arg.get_value())
                else:
                    self.raise_parse_error(msg="there is no closing paren in the end of input statement")
            else:
                self.raise_parse_error(msg="there is no identifier in input statement")
        else:
            return None

    def get_communicate_statement(self):
        # try to parse input statement
        statement = self.get_input_statement()
        if statement:
            return statement
        # try to parse output statement
        statement = self.get_output_statement()
        if statement:
            return statement
        return None

    def get_var_create_statement(self):
        # start with datatype
        if self.token_type_is_datatype():
            var_type = self.token
            self.next_token()
            # next identifier of new creating var
            if self.token_type_is(TokenType.T_IDENTIFIER):
                var_identifier = self.token 
                self.next_token()
                # should end with )
                if self.token_type_is(TokenType.T_RPAREN):
                    self.next_token()
                    return VarCreateStatement(var_type=var_type.get_type(), var_identifier=var_identifier.get_value())
                else:
                    self.raise_parse_error(msg="There is no closing paren in var creae statement")
            else:
                self.raise_parse_error(msg="there is no identificaor in var create statement")
        else:
            return None

    def get_var_assignment_statement(self):
        # start with =
        if self.token_type_is(TokenType.T_ASSIGNMENT):
            self.next_token()
            # next identifier of var where to write
            if self.token_type_is(TokenType.T_IDENTIFIER):
                # next value to write
                var_identifier = self.token
                self.next_token()
                # as literal or identifier
                if self.token_type_is_literal() or self.token_type_is(TokenType.T_IDENTIFIER):
                    var_value = self.token
                    self.next_token()
                    if self.token_type_is(TokenType.T_RPAREN):
                        self.next_token()
                        if var_value.token_type == TokenType.T_IDENTIFIER:
                            return AssignmentStatement(var_identifier=var_identifier.get_value(), var_value=self.build_identifier_obj(var_value))
                        else:
                            return AssignmentStatement(var_identifier=var_identifier.get_value(), var_value=self.build_literal_obj(var_value))
                    else:
                        self.raise_parse_error(msg="there is no closing paren in the end of assignment statement")
                # as literal or identifier
                if self.token_type_is(TokenType.T_LPAREN):
                    self.next_token()
                    statement = self.get_fun_call_statement()
                    # as fun call
                    if statement:
                        if self.token_type_is(TokenType.T_RPAREN):
                            self.next_token()
                            return AssignmentStatement(var_identifier=var_identifier.get_value(), var_value=statement)
                        else:
                            self.raise_parse_error(msg="there is no closing paren in the end of assignment statement")
                    # as arithmetic
                    statement = self.get_arithmetic_statement()
                    if statement:
                        if self.token_type_is(TokenType.T_RPAREN):
                            self.next_token()
                            return AssignmentStatement(var_identifier=var_identifier.get_value(), var_value=statement)
                        else:
                            self.raise_parse_error(msg="there is no closing paren in the end of assignment statement")
                    # as condition
                    statement = self.get_condition_statement()
                    if statement:
                        if self.token_type_is(TokenType.T_RPAREN):
                            self.next_token()
                            return AssignmentStatement(var_identifier=var_identifier.get_value(), var_value=statement)
                        else:
                            self.raise_parse_error(msg="there is no closing paren in the end of assignment statement")
                    # as concat
                    statement = self.get_concat_statement()
                    if statement:
                        if self.token_type_is(TokenType.T_RPAREN):
                            self.next_token()
                            return AssignmentStatement(var_identifier=var_identifier.get_value(), var_value=statement)
                        else:
                            self.raise_parse_error(msg="there is no closing paren in the end of assignment statement")
                    self.raise_parse_error(msg="invalid 2nd argument in assignment statement")
            else:
                self.raise_parse_error(msg="thre is no identifier afer = in assignment satement")
        else:
            return None

    def get_fun_call_statement(self):
        # start with proper keyword
        if self.token_type_is(TokenType.T_IDENTIFIER):
            # next identifier of funcall to call
            fun_identifier = self.token
            self.next_token()
            # read args for run calling
            fun_args = []
            # end with )
            while (not self.token_type_is(TokenType.T_RPAREN)):
                fun_args.append(self.get_arg_for_fun_calling())
            self.next_token()
            return FunCallStatement(fun_identifier=fun_identifier.get_value(), fun_args=fun_args)
        else:
            return None

    def get_arg_for_fun_calling(self):
        # arg to pass when fun calling
        # as literal
        if self.token_type_is_literal():
            value = self.token
            self.next_token()
            return FunCallArg(fun_call_arg=self.build_literal_obj(value))
        # as identifier
        elif self.token_type_is(TokenType.T_IDENTIFIER):
            value = self.token
            self.next_token()
            return FunCallArg(fun_call_arg=self.build_identifier_obj(value))
        # as another statement
        elif self.token_type_is(TokenType.T_LPAREN):
            self.next_token()
            # as fun call
            statement = self.get_fun_call_statement()
            if statement:
                return FunCallArg(fun_call_arg=statement)
            # as arithmetic
            statement = self.get_arithmetic_statement()
            if statement:
                return FunCallArg(fun_call_arg=statement)
            # as concat
            statement = self.get_concat_statement()
            if statement:
                return FunCallArg(fun_call_arg=statement)
            # as condition
            statement = self.get_condition_statement()
            if statement:
                return FunCallArg(fun_call_arg=statement)
            self.raise_parse_error(msg="invalid argument for fun call")
        else:
            self.raise_parse_error(msg="invalid argument for fun call")

    def get_arithmetic_statement(self):
        # start with arithmetic operator + - * /
        if self.token_type_is_arithm_op():
            action_token = self.token
            self.next_token()
            # first arithmetic arg
            first_arithm_arg = self.get_arithmetic_arg()
            # second arithmetic arg
            second_arithm_arg = self.get_arithmetic_arg()
            # should end with )
            if self.token_type_is(TokenType.T_RPAREN): 
                self.next_token()
                return ArithmeticStatement(operator=action_token.get_value(), first_arithm_arg=first_arithm_arg, second_arithm_arg=second_arithm_arg)
            else:
                self.raise_parse_error(msg="there is no closing paren in the end of arithmetic statement")
        else:
            return None

    def get_arithmetic_arg(self):
        # arithmetic argument
        # as number
        if self.token_type_is_number():
            value = self.token
            self.next_token()
            return ArithmeticArg(arithmetic_arg=self.build_number_obj(value))

        # as identifier
        if self.token_type_is(TokenType.T_IDENTIFIER):
            value = self.token
            self.next_token()
            return ArithmeticArg(arithmetic_arg=self.build_identifier_obj(value))
        
        # as another statement
        if self.token_type_is(TokenType.T_LPAREN):
            self.next_token()
            # as fun call
            statement = self.get_fun_call_statement()
            if statement:
                return ArithmeticArg(arithmetic_arg=statement)
            # as arithmetic
            statement = self.get_arithmetic_statement()
            if statement:
                return ArithmeticArg(arithmetic_arg=statement)
            # as condition
            statement = self.get_condition_statement()
            if statement:
                return ArithmeticArg(arithmetic_arg=statement)
            self.raise_parse_error(msg="invalid arithmetic statement argument")
        else:
            self.raise_parse_error(msg="invalid arithmetic argument")

    def token_type_is_arithm_op(self):
        return (
            self.token_type_is(TokenType.T_PLUS) or
            self.token_type_is(TokenType.T_MINUS) or
            self.token_type_is(TokenType.T_MULTIPLY) or
            self.token_type_is(TokenType.T_DIVIDE)
        )
               

    def token_type_is(self, token_type):
        return self.token.get_type() == token_type
        
    def next_token(self):
        self.token = self.lexer.get_next_token()
        if self.token_type_is(TokenType.T_ERROR):
            raise LexerError(msg=self.token.error.error_msg , row=self.token.error.pos_row, col=self.token.error.pos_col, code=self.token.error.error_code)


    def raise_parse_error(self, msg, code=None):
        raise ParserError(msg=msg, row=self.token.pos_row, col=self.token.pos_col, code=code)