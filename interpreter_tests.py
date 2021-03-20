import unittest
from my_token import *
from lexer import *
from parser import *
from interpreter import *
from program import *
from source import *
from statement import *
from elements import *

#
# Unit Tests for Parser
#

def execute_program(source_str):
    lexer = Lexer(SourceString(source_str))
    parser = Parser(lexer)
    program = parser.parse_program()
    interpreter = Interpreter(program)
    interpreter.execute()
    return interpreter.env

class TestInterpreter(unittest.TestCase): 

    def test_create_var(self):
        env = execute_program("(int a)")
        self.assertTrue(env.get_var("a"))

    def test_assign_var(self):
        env = execute_program("(int a) (= a 3)")
        self.assertEqual(env.get_var_value("a"), 3)

    def test_def_fun(self):
        env = execute_program("(fun get_txt txt (int n) {(ret 'a')})(get_txt 1)")
        self.assertTrue(env.get_fun("get_txt"))

    def test_recreate_fun_def_will_raise_error(self):
         with self.assertRaises(InterpreterError):
            execute_program("(fun get_txt txt (int n) {(ret 'a')})(fun get_txt txt (int n) {(ret 'a')})(get_txt 1)")

    def test_recreate_var_will_raise_error(self):
        with self.assertRaises(InterpreterError):
            execute_program("(int a)(int a)")

    def test_recreate_var_in_context_block_is_allowed(self):
        execute_program("(int a)(if (1) {(int a)})")

    def test_reference_to_var_before_assignment_will_raise_error(self):
        with self.assertRaises(InterpreterError):
            env = execute_program("(int a)(+ a 3)")

    def test_reference_to_unexisted_var_will_raise_error(self):
        with self.assertRaises(InterpreterError):
            env = execute_program("(+ a 3)")

    def test_using_not_numbers_in_arithmetic_will_raise_error(self):
        with self.assertRaises(InterpreterError):
            execute_program("(txt t)(= t 'a')(+ 1 t)")    

    def test_wrong_num_of_args_when_fun_call_calling_will_raise_error(self):
        with self.assertRaises(InterpreterError):
            execute_program("(fun get_txt txt (int n) {(ret 'a')})(get_txt 1 2)")

    def test_using_not_strings_in_concat_will_raise_error(self):
        with self.assertRaises(InterpreterError):
            execute_program("(fun get_txt int {(ret 1)})(. 'asd' (get_txt))") 

    def test_binarycomparison_first_arg_string_sec_num_will_raise_error(self):
        with self.assertRaises(InterpreterError):
            execute_program("(< 'asd' 1)") 

    def test_binarycomparison_first_arg_num_sec_string_will_raise_error(self):
        with self.assertRaises(InterpreterError):
            execute_program("(< 1 'asd')") 

    def test_conversion_from_real_to_int_will_raise_error(self):
        with self.assertRaises(InterpreterError):
            execute_program("(int n)(= n 1.2)") 

    def test_conversion_from_real_to_roman_will_raise_error(self):
        with self.assertRaises(InterpreterError):
            execute_program("(rom n)(= n 1.2)") 

    def test_conversion_from_int_to_roman_will_raise_error(self):
        with self.assertRaises(InterpreterError):
            execute_program("(rom n)(= n 1)") 

    def test_max_absolute_value_exceeded_will_raise_error_int(self):
        with self.assertRaises(InterpreterError):
            execute_program("(int n)(= n (* 999999 999999))") 

    def test_max_absolute_value_exceeded_will_raise_error_roman(self):
        with self.assertRaises(InterpreterError):
            execute_program("(rom n)(= n (* MMM MMM))") 


unittest.main()