from inode import *

class Statement(INode):
   def __init__(self):
      self.start_pos_row = -1
      self.start_pos_col = -1

class AssignmentStatement(Statement):
    def __init__(self, var_identifier, var_value):
        self.var_identifier = var_identifier
        self.var_value = var_value
        # print("__Assignment Statement")

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return self.var_identifier == other.var_identifier and self.var_value == other.var_value

class VarCreateStatement(Statement):
    def __init__(self, var_type, var_identifier):
        self.var_type = var_type
        self.var_identifier = var_identifier
        # print("__Var create Statement")

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return self.var_type == other.var_type and self.var_identifier == other.var_identifier

class InputStatement(Statement):
    def __init__(self, input_arg):
        self.input_arg = input_arg
        # print("__Input Statement")

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return self.input_arg == other.input_arg

class OutputStatement(Statement):
    def __init__(self, output_arg):
        self.output_arg = output_arg
        # print("__Output Statement")

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return self.output_arg == other.output_arg

class ArithmeticStatement(Statement):
    def __init__(self, operator, first_arithm_arg, second_arithm_arg):
        self.operator = operator
        self.first_arithm_arg = first_arithm_arg
        self.second_arithm_arg = second_arithm_arg
        # print("__Arithmetic Statement")

    def accept(self, visitor):
        visitor.visit(self)

    def __eq__(self, other):
        return (
           self.operator == other.operator and
           self.first_arithm_arg == other.first_arithm_arg and
           self.second_arithm_arg == other.second_arithm_arg
           )

class IfStatement(Statement):
     def __init__(self, condition, block):
        self.condition = condition
        self.block = block
        # print("__If Statement")

     def accept(self, visitor):
        visitor.visit(self)
     
     def __eq__(self, other):
        return (
           self.condition == other.condition and
           self.block == other.block 
           )

class IfElseStatement(Statement):
     def __init__(self, condition, block_true, block_false):
        self.condition = condition
        self.block_true = block_true
        self.block_false = block_false
        # print("__IfElse Statement")      

     def accept(self, visitor):
        visitor.visit(self) 

     def __eq__(self, other):
        return (
           self.condition == other.condition and
           self.block_true == other.block_true and
           self.block_false == other.block_false
           )

class RepeatStatement(Statement):
     def __init__(self, condition, block):
        self.condition = condition
        self.block = block
        # print("__Repeat Statement") 

     def accept(self, visitor):
        visitor.visit(self)

     def __eq__(self, other):
        return (
           self.condition == other.condition and
           self.block == other.block 
           )

class FunCallStatement(Statement):
     def __init__(self, fun_identifier, fun_args):
        self.fun_identifier = fun_identifier
        self.fun_args = fun_args
        # print("__Fun call Statement") 

     def accept(self, visitor):
        visitor.visit(self)

     def __eq__(self, other):
        if len(self.fun_args) != len(other.fun_args):
           return False
        for i in range (len(self.fun_args)):
           if self.fun_args[i] != other.fun_args[i]:
              return False
        return self.fun_identifier == other.fun_identifier


class FunDefStatement(Statement):
     def __init__(self, fun_identifier, return_type, args, fun_block):
        self.fun_identifier = fun_identifier
        self.return_type = return_type
        self.args = args
        self.fun_block = fun_block
        # print("__Fun def Statement")

     def accept(self, visitor):
        visitor.visit(self)
      
     def __eq__(self, other):
        if len(self.args) != len(other.args):
           return False
        for i in range (len(self.args)):
           if self.args[i] != other.args[i]:
              return False
        return (
           self.fun_identifier == other.fun_identifier and
           self.return_type == other.return_type and
           self.fun_block == other.fun_block
           )

class ReturnStatement(Statement):
     def __init__(self, return_arg):
        self.return_arg = return_arg
        # print("__Return Statement")

     def accept(self, visitor):
        visitor.visit(self)
      
     def __eq__(self, other):
        return (
           self.return_arg == other.return_arg 
           )

class ConcatStatement(Statement):
     def __init__(self, first_concat_arg, second_concat_arg):
        self.first_concat_arg = first_concat_arg
        self.second_concat_arg = second_concat_arg
        # print("__Concat Statement")
        
     def accept(self, visitor):
        visitor.visit(self)

     def __eq__(self, other):
        return (
           self.first_concat_arg == other.first_concat_arg and
           self.second_concat_arg == other.second_concat_arg
           )

class ConditionStatement(Statement):
     def __init__(self, condition):
        self.condition = condition
        # print("__Condition Statement")

     def accept(self, visitor):
        visitor.visit(self)

     def __eq__(self, other):
        return (
           self.condition == other.condition 
           )

        