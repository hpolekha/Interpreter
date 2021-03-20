import math     
from multipledispatch import dispatch
from inodevisitor import *
from statement import *
from elements import *
from program import *
from enviroment import *
from env_elements import *
from limits import *
from errors import *

class Interpreter(INodeVisitor):
    def __init__(self, program):
        self.program = program
        self.env = Enviroment(self)
        self.return_detected = False
        self.cur_statement_start_row = -1
        self.cur_statement_start_col = -1

    def execute(self):
        try:
            self.program.accept(self)
        except OwnError as ex:
            raise ex
            
    @dispatch(Program)
    def visit(self, program):
        for statement in program.statements:
            # save info about when statement starts for error log
            self.cur_statement_start_row = statement.start_pos_row
            self.cur_statement_start_col = statement.start_pos_col
            statement.accept(self)

    @dispatch(AssignmentStatement)
    def visit(self, statement):
        # print("__Assignment") 
        # will place its final value in self.env.last_result
        statement.var_value.accept(self)
        # set var value
        self.env.set_var(statement.var_identifier, self.env.get_last_result())
    
    @dispatch(VarCreateStatement)
    def visit(self, statement):
        # print("__VarCreate")
        self.env.create_var(statement.var_type, statement.var_identifier)

    @dispatch(InputStatement)
    def visit(self, statement):
        # print("__Input")
        input_value = input()
        # allow_convert=True for trying convert string to var_type
        self.env.set_var(statement.input_arg, input_value, allow_convert=True)

    @dispatch(OutputStatement)
    def visit(self, statement):
        # print("__Output")
        # will place its final value in self.env.last_result
        statement.output_arg.accept(self)
        # convert print value to roman format if is roman
        if self.env.last_result_is_roman:
            print(self.to_roman(self.env.get_last_result()))
        else:
            print(self.env.get_last_result())
    
    # convert dec to roman string
    def to_roman(self, value):
        dec = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
            ]
        roman = [
            "M", "CM", "D", "CD",
            "C", "XC", "L", "XL",
            "X", "IX", "V", "IV",
            "I"
            ]

        roman_str = ''
        i = 0
        # get num of thousands than hundreds etc
        # put proper roman symbol from roman the right number of time to string result
        while value > 0:
            div = value // dec[i]
            while div:
                roman_str += roman[i]
                value -= dec[i]
                div -= 1
            i += 1
        return roman_str

    @dispatch(ArithmeticStatement)
    def visit(self, statement):
        # print("__Arithmetic")
        # initally set the result is integer type(value) and roman
        result_in_roman = True
        result_int = True

        # will place its final value in self.env.last_result
        statement.first_arithm_arg.accept(self)
        first_arg = self.env.get_last_result()

        # raise error if self.env.last_result is not a number
        if self.is_not_number(first_arg):
            self.raise_interpreter_error(msg="Invalid arithmetic arg: " + first_arg)

        # if arg is not roman number, then result will not be of roman type
        if not self.env.last_result_is_roman:
            result_in_roman = False
        
        # if arg is not integer number, then result will not be of int type
        if not isinstance(self.env.get_last_result(), int):
            result_int = False

        # will place its final value in self.env.last_result
        statement.second_arithm_arg.accept(self)
        second_arg = self.env.get_last_result()

        # raise error if self.env.last_result is not a number
        if self.is_not_number(second_arg):
            self.raise_interpreter_error(msg="Invalid arithmetic arg: " + second_arg)

        # if arg is not roman number, then result will not be of roman type
        if not self.env.last_result_is_roman:
            result_in_roman = False
        
        # if arg is not integer number, then result will not be of int type
        if not isinstance(self.env.get_last_result(), int):
            result_int = False

        # calculate result and put in self.env.last_result
        if statement.operator == '+':
            self.env.set_last_result(first_arg + second_arg)
        elif statement.operator == '-':
            self.env.set_last_result(first_arg - second_arg)
        elif statement.operator == '*':
            self.env.set_last_result(first_arg * second_arg)
        elif statement.operator == '/':
            self.env.set_last_result(first_arg / second_arg)

        # mark last_result as roman if args are roman and result does not axceed roman value limit and does not equal to 0
        if result_in_roman and abs(self.env.get_last_result()) <= MAX_ROMAN_ABSOLUTE_VALUE and self.env.get_last_result() != 0:
            self.env.last_result_is_roman  = True

        # make right int from float if result must be of int type
        if result_int:
            # math.floor return int
            self.env.set_last_result(math.floor(self.env.get_last_result()) if self.env.get_last_result() > 0 else math.ceil(self.env.get_last_result()))
    
    def is_not_number(self, value):
        return (
            not isinstance(value, int) and
            not isinstance(value, float)
        )

    @dispatch(IfStatement)
    def visit(self, statement):
        # print("__If")
        
        # will place its final value in self.env.last_result - 0 or 1 of int type
        statement.condition.accept(self)
        # do block if condition is True
        if self.env.get_last_result():
            statement.block.accept(self)

    
    @dispatch(IfElseStatement)
    def visit(self, statement):
        # print("__IfElse")
        
        # will place its final value in self.env.last_result - 0 or 1 of int type
        statement.condition.accept(self)
        # do block_true if condition is True
        if self.env.get_last_result():
            statement.block_true.accept(self)
        # do block_true if condition is False
        else:
            statement.block_false.accept(self)

    @dispatch(RepeatStatement)
    def visit(self, statement):
        # print("__Repeat")
        
        # will place its final value in self.env.last_result - 0 or 1 of int type
        statement.condition.accept(self)
        # do block while condition is True
        while self.env.get_last_result():
            statement.block.accept(self)
            # update condition value
            statement.condition.accept(self)
    
    @dispatch(FunCallStatement)
    def visit(self, statement):
        # print("__FunCall")
        
        # will raise error if fun with this name does not exist 
        function = self.env.get_fun(statement.fun_identifier)
        
        # compare number of arg required for calling and used while calling
        # rase error if they are differentif len(statement.fun_args) != len(function.args):
        if len(statement.fun_args) != len(function.args):
            self.raise_interpreter_error(msg="expected " + str(len(function.args)) + " args, " + str(len(statement.fun_args)) + " were given")

        # prepare vars for creating in new callcontext
        vars = []
        for i in range (len(statement.fun_args)):
            # will place arg's final value in self.env.last_result
            statement.fun_args[i].accept(self)
            arg_value = self.env.get_last_result()
            # erase error if actual call arg type is not right for fun call arg type
            self.env.parse_value_to(arg_value, function.args[i].var_type)
            vars.append([function.args[i].var_type, function.args[i].var_identifier, arg_value])

        # create new call_context
        self.env.create_call_context()
        # create vars from fun calling args
        for var in vars:
            self.env.create_var(var[0], var[1], var[2])
            pass
        # do block
        function.block.accept(self)
        # reset return_detected for nested fun calls
        self.return_detected = False
        # erase error if return type is not right for fun def return type
        self.env.parse_value_to(self.env.get_last_result(), function.return_type)
        # delete call context
        self.env.delete_call_context()

    @dispatch(FunDefStatement)
    def visit(self, statement):
        # print("__FunDef")
        # will raise error w=if fun with the same name does alreaady exist
        self.env.create_fun(identifier=statement.fun_identifier, return_type=statement.return_type, args=statement.args, block=statement.fun_block)

    @dispatch(ReturnStatement)
    def visit(self, statement):
        # print("__Ret")
        statement.return_arg.accept(self)
        # activate flag return_detected for interrupticg funblock executing
        self.return_detected = True

    
    @dispatch(ConcatStatement)
    def visit(self, statement):
        # print("__Concat")
        # will place its final value in self.env.last_result
        statement.first_concat_arg.accept(self)
        first_arg = self.env.get_last_result()
        # rase error if first arg is not string
        if not isinstance(first_arg, str):
            self.raise_interpreter_error(msg="Invalid concat argument: " + str(first_arg))
        
        # will place its final value in self.env.last_result
        statement.second_concat_arg.accept(self)
        second_arg = self.env.get_last_result()
        # rase error if second arg is not string
        if not isinstance(second_arg, str):
            self.raise_interpreter_error(msg="Invalid concat argument: " + str(second_arg))
        
        # update env with result info
        self.env.set_last_result(first_arg + second_arg)
        self.env.last_result_is_roman = False

    @dispatch(ConditionStatement)
    def visit(self, statement):
        # print("__ConditionStatement")
        # will place its final value in self.env.last_result
        statement.condition.accept(self)
        # convert to represanting bool in int
        self.env.set_last_result(1 if self.env.get_last_result() else 0)
        # result's type is int
        self.env.last_result_is_roman = False

    @dispatch(TextLiteral)
    def visit(self, el):
        # write own value into self.env.last_result
        self.env.set_last_result(el.value)
        # mark as not roman value
        self.env.last_result_is_roman = False
    
    @dispatch(IntLiteral)
    def visit(self, el):
        # write own value into self.env.last_result
        self.env.set_last_result(el.value)
        # mark as not roman value
        self.env.last_result_is_roman = False

    @dispatch(RealLiteral)
    def visit(self, el):
        # write own value into self.env.last_result
        self.env.set_last_result(el.value)
        # mark as not roman value
        self.env.last_result_is_roman = False

    @dispatch(RomanLiteral)
    def visit(self, el):
        # write own value into self.env.last_result
        self.env.set_last_result(el.value)
        # mark as not roman value
        self.env.last_result_is_roman = True

    @dispatch(Identifier)
    def visit(self, el):
        # get value of var
        # will erase error if var foes not exist
        var_value = self.env.get_var_value(el.value)
        # write var_value into self.env.last_result
        # will mark is it roman or not 
        self.env.set_last_result(var_value)

    @dispatch(Void)
    def visit(self, el):
        # write own value into self.env.last_result
        self.env.set_last_result(el.value)
        # mark as not roman value
        self.env.last_result_is_roman = False

    @dispatch(ConcatArg)
    def visit(self, el):
        el.concat_arg.accept(self)
        
    @dispatch(ArithmeticArg)
    def visit(self, el):
        el.arithmetic_arg.accept(self)

    @dispatch(Condition)
    def visit(self, el):
        # will place its final value in self.env.last_result
        el.condition.accept(self)
        # convert to represanting bool in int
        self.env.set_last_result(1 if self.env.get_last_result() else 0)
        # result's type is int
        self.env.last_result_is_roman = False

    @dispatch(ConditionArg)
    def visit(self, el):
        el.condition_arg.accept(self)

    @dispatch(UnaryComparison)
    def visit(self, el):
        # will place its final value in self.env.last_result
        el.condition_arg.accept(self) 
        arg = self.env.get_last_result()
        if el.comp_operator == '!':
            # update info about last result
            self.env.set_last_result(not arg)
            self.env.last_result_is_roman = False
        else:
            self.raise_interpreter_error(msg="Unknown unary comaprison operator: " + str(el.comp_operator))

    @dispatch(BinaryComparison)
    def visit(self, el):
        # will place its final value in self.env.last_result
        el.first_condition_arg.accept(self) 
        first_arg = self.env.get_last_result()
        # will place its final value in self.env.last_result
        el.second_condition_arg.accept(self)
        second_arg = self.env.get_last_result()

        # both args should be str or both args shoud be not str, raise error otherwise
        if isinstance(first_arg, str):
            if not isinstance(second_arg, str):
                self.raise_interpreter_error(msg="Invalid condition expression args format: " + str(second_arg))
        else:
            if isinstance(second_arg, str):
                self.raise_interpreter_error(msg="Invalid condition expression args format: " + str(second_arg))

        # calculate result and write into self.env.last_result
        if el.comp_operator == '<':
            self.env.set_last_result(first_arg < second_arg)
        elif el.comp_operator == '>':
            self.env.set_last_result(first_arg > second_arg) 
        elif el.comp_operator == '<=':
            self.env.set_last_result(first_arg <= second_arg) 
        elif el.comp_operator == '>=':
            self.env.set_last_result(first_arg >= second_arg) 
        elif el.comp_operator == '==':
            self.env.set_last_result(first_arg == second_arg) 
        elif el.comp_operator == '!=':
            self.env.set_last_result(first_arg != second_arg) 
        else:
            self.raise_interpreter_error(msg="Unknown binary comaprison operator: " + str(el.comp_operator))
        # update info about last result
        self.env.last_result_is_roman = False

    @dispatch(LogComparison)
    def visit(self, el):
        # will place its final value in self.env.last_result
        el.first_condition_arg.accept(self) 
        first_arg = self.env.get_last_result()
        # will place its final value in self.env.last_result
        el.second_condition_arg.accept(self)
        second_arg = self.env.get_last_result()

        # both args should be str or both args shoud be not str, raise error otherwise
        if isinstance(first_arg, str):
            if not isinstance(second_arg, str):
                self.raise_interpreter_error(msg="Invalid condition expression args format: " + str(second_arg))
        else:
            if isinstance(second_arg, str):
                self.raise_interpreter_error(msg="Invalid condition expression args format: " + str(second_arg))

        # calculate result and write into self.env.last_result
        if el.log_operator == 'or':
            self.env.set_last_result(first_arg or second_arg)
        elif el.log_operator == 'and':
            self.env.set_last_result(first_arg and second_arg) 
        else:
            self.raise_interpreter_error(msg="Unknown log comaprison operator: " + str(el.log_operator))
        # update info about last result
        self.env.last_result_is_roman = False

    @dispatch(Block)
    def visit(self, el):
        # create block context for vars
        self.env.create_block_context()
        # do statements until return statement will detected or there will be no more statements
        for statement in el.statements:
            statement.accept(self)
            if self.return_detected:
                break
        self.env.delete_block_context()

        
    @dispatch(FunBlock)
    def visit(self, el):
        # block context already created by creating call context
        # do statements until return statement will detected or there will be no more statements
        for statement in el.statements:
            statement.accept(self)
            if self.return_detected:
                self.return_detected = False
                break

    @dispatch(FunCallArg)
    def visit(self, el):
        # write own value into self.env.last_result
        el.fun_call_arg.accept(self)

    def raise_interpreter_error(self, msg, code=None):
        raise  InterpreterError(msg=msg, row=self.cur_statement_start_row, col=self.cur_statement_start_col, code=code)

    def raise_error(self, msg, code=None):
        self.raise_interpreter_error(msg=msg, code=code)
