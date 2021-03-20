from inode import *
from errors import *
import re

class ArithmeticArg(INode):
    def __init__(self, arithmetic_arg):
        self.arithmetic_arg = arithmetic_arg
        # print("__Arithmetic Arg")

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return self.arithmetic_arg == other.arithmetic_arg

class Condition(INode):
    def __init__(self, condition):
        self.condition = condition
        # print("__Conditon")

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return (
           self.condition == other.condition 
           )

class ConditionArg(INode):
    def __init__(self, condition_arg):
        self.condition_arg = condition_arg
        # print("__Condition arg")

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return (
           self.condition_arg == other.condition_arg 
           )

class Block(INode):
    def __init__(self, statements):
        self.statements = statements
        # print("__Block")

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        # num of statements should be equal in both blocks
        if len(self.statements) != len(other.statements):
           return False
        for i in range (len(self.statements)):
           # each statemenet should be equal
           if self.statements[i] != other.statements[i]:
              return False
        return True

class FunCallArg(INode):
    def __init__(self, fun_call_arg):
        self.fun_call_arg = fun_call_arg
        # print("__Fun Call Arg")

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return (
           self.fun_call_arg == other.fun_call_arg 
           )

class FunBlock(INode):
    def __init__(self, statements):
        self.statements = statements
        # print("__Fun block")

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        # num of statements should be equal in both blocks
        if len(self.statements) != len(other.statements):
           return False
        for i in range (len(self.statements)):
           # each statemenet should be equal
           if self.statements[i] != other.statements[i]:
              return False
        return True

class FunDefArg:
    def __init__(self, var_type, var_identifier):
        self.var_type = var_type
        self.var_identifier = var_identifier
        # print("__Fun def arg")

    def __eq__(self, other):
        return (
           self.var_type == other.var_type and
           self.var_identifier == other.var_identifier 
           )

class ConcatArg(INode):
    def __init__(self, concat_arg):
        self.concat_arg = concat_arg
        # print("__Concat arg")

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return self.concat_arg == other.concat_arg

class UnaryComparison(INode):
    def __init__(self, comp_operator, condition_arg):
        self.comp_operator = comp_operator
        self.condition_arg = condition_arg
        # print("__Unary Compariosn")

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return (
           self.comp_operator == other.comp_operator and
           self.condition_arg == other.condition_arg 
           )

class BinaryComparison(INode):
    def __init__(self, comp_operator, first_condition_arg, second_condition_arg):
        self.comp_operator = comp_operator
        self.first_condition_arg = first_condition_arg
        self.second_condition_arg = second_condition_arg
        # print("__Binary Compariosn")

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return (
           self.comp_operator == other.comp_operator and
           self.first_condition_arg == other.first_condition_arg and
           self.second_condition_arg == other.second_condition_arg
           )

class LogComparison(INode):
    def __init__(self, log_operator, first_condition_arg, second_condition_arg):
        self.log_operator = log_operator
        self.first_condition_arg = first_condition_arg
        self.second_condition_arg = second_condition_arg
        # print("__Log Compariosn")

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return (
           self.log_operator == other.log_operator and
           self.first_condition_arg == other.first_condition_arg and
           self.second_condition_arg == other.second_condition_arg
           )

class TextLiteral(INode):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return self.value == other.value

class IntLiteral(INode):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return self.value == other.value

class RealLiteral(INode):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return self.value == other.value

class RomanLiteral(INode):
    def __init__(self, value):
        self.value = self.convert_from_roman(value)

    def convert_from_roman(self, value):
        # check if roman string is in correct format
        # regex for max 9999 number
        # row and col will be overwritten by parser
        # make sure to work with string
        value = str(value).upper()
        if not value:
            raise ParserError("Invalid rom number", row=-1, col=-1)
        if not re.search(r"^(-)?M{0,9}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", value):
            raise ParserError("Invalid rom number", row=-1, col=-1)
        
        # remember about minus at the begining of negative roman number
        # but remove it for calculating absolute roman value
        is_negative = False
        if value[0] == '-':
            is_negative = True
            value = value[1:]

        roman_dict = {
            'I': 1, 
            'V': 5, 
            'X': 10, 
            'L': 50, 
            'C': 100, 
            'D': 500, 
            'M': 1000
        }
        int_value = 0
        for i in range(len(value)):
            if i > 0 and roman_dict[value[i]] > roman_dict[value[i - 1]]:
                int_value += roman_dict[value[i]] - 2 * roman_dict[value[i - 1]]
            else:
                int_value += roman_dict[value[i]]

        # if there was minus symbol at the begining, make roman num negative
        if is_negative:
            int_value *= -1

        return int_value


    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return self.value == other.value

class Identifier(INode):
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return self.value == other.value

class Void(INode):
    def __init__(self, value=None):
        self.value = value

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return self.value == other.value