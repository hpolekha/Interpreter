import unittest
from my_token import *
from lexer import *
from parser import *
from source import *
from statement import *
from elements import *

#
# Unit Tests for Parser
#

def parse_program(source_str):
    lexer = Lexer(SourceString(source_str))
    parser = Parser(lexer)
    program = parser.parse_program()
    return program.statements[-1]

class TestParser(unittest.TestCase): 


    def test_input_statement(self):
        self.assertEqual(parse_program("(read a)"), InputStatement(input_arg='a'))

    def test_var_create_statement_int(self):
        self.assertEqual(parse_program("(int a)"), VarCreateStatement(var_type=TokenType.T_INT, var_identifier='a'))

    def test_var_create_statement_real(self):
        self.assertEqual(parse_program("(real a)"), VarCreateStatement(var_type=TokenType.T_REAL, var_identifier='a'))

    def test_var_create_statement_roman(self):
        self.assertEqual(parse_program("(rom a)"), VarCreateStatement(var_type=TokenType.T_ROM, var_identifier='a'))

    def test_var_create_statement_text(self):
        self.assertEqual(parse_program("(txt a)"), VarCreateStatement(var_type=TokenType.T_TXT, var_identifier='a'))
    
    def test_var_assign_statement_int(self):
        self.assertEqual(parse_program("(= a 3)"), AssignmentStatement(var_identifier='a', var_value=IntLiteral(value=3)))
    
    def test_var_assign_statement_real(self):
        self.assertEqual(parse_program("(= a 3.1)"), AssignmentStatement(var_identifier='a', var_value=RealLiteral(value=3.1)))
    
    def test_var_assign_statement_roman(self):
        self.assertEqual(parse_program("(= a xviii)"), AssignmentStatement(var_identifier='a', var_value=RomanLiteral(value="xviii")))

    def test_var_assign_statement_text(self):
        self.assertEqual(parse_program("(= a 'asd')"), AssignmentStatement(var_identifier='a', var_value=TextLiteral(value='asd')))

    def test_var_assign_statement_var(self):
        self.assertEqual(parse_program("(= a b)"), AssignmentStatement(var_identifier='a', var_value=Identifier(value='b')))


    def test_output_statement_int(self):
        self.assertEqual(parse_program("(write 1)"), OutputStatement(output_arg=IntLiteral(value=1)))

    def test_output_statement_real(self):
        self.assertEqual(parse_program("(write 1.1)"), OutputStatement(output_arg=RealLiteral(value=1.1)))

    def test_output_statement_roman(self):
        self.assertEqual(parse_program("(write x)"), OutputStatement(output_arg=RomanLiteral(value='x')))

    def test_output_statement_var(self):
        self.assertEqual(parse_program("(write a)"), OutputStatement(output_arg=Identifier('a')))

    def test_arithm_statement_plus(self):
        self.assertEqual(parse_program("(+ 1 2)"), ArithmeticStatement(operator="+",  first_arithm_arg=ArithmeticArg(IntLiteral(1)), second_arithm_arg=ArithmeticArg(IntLiteral(2))))

    def test_arithm_statement_minus(self):
        self.assertEqual(parse_program("(- 1 2)"), ArithmeticStatement(operator="-",  first_arithm_arg=ArithmeticArg(IntLiteral(1)), second_arithm_arg=ArithmeticArg(IntLiteral(2))))

    def test_arithm_statement_mult(self):
        self.assertEqual(parse_program("(* 1 2)"), ArithmeticStatement(operator="*",  first_arithm_arg=ArithmeticArg(IntLiteral(1)), second_arithm_arg=ArithmeticArg(IntLiteral(2))))

    def test_arithm_statement_div(self):
        self.assertEqual(parse_program("(/ 1 2)"), ArithmeticStatement(operator="/",  first_arithm_arg=ArithmeticArg(IntLiteral(1)), second_arithm_arg=ArithmeticArg(IntLiteral(2))))

    def test_concat_statement(self):
        self.assertEqual(parse_program("(. 'a' 'b')"), ConcatStatement(first_concat_arg=ConcatArg(TextLiteral('a')), second_concat_arg=ConcatArg(TextLiteral('b'))))

    def test_if_statement(self):
        self.assertEqual(parse_program("(if (1) {})"), IfStatement(condition=Condition(IntLiteral(1)), block=Block([])))

    def test_if_statement_block(self):
        self.assertEqual(parse_program("(if (1) {(write a)})"), IfStatement(condition=Condition(IntLiteral(1)), block=Block([OutputStatement(output_arg
        =Identifier('a'))])))

    def test_if_else_statement(self):
        self.assertEqual(parse_program("(ifel (1) {(write 1)}{(write a)})"), IfElseStatement(condition=Condition(IntLiteral(1)), block_true=Block([OutputStatement(output_arg=IntLiteral(1))]), block_false=Block([OutputStatement(output_arg=Identifier('a'))])))

    def test_repeat_statement(self):
        self.assertEqual(parse_program("(loop (1) {})"), RepeatStatement(condition=Condition(IntLiteral(1)), block=Block([])))

    def test_condition_statement_unary(self):
        self.assertEqual(parse_program("(! 1)"), ConditionStatement(condition=UnaryComparison(comp_operator='!', condition_arg=ConditionArg(IntLiteral(1)))))

    def test_condition_statement_binary_less(self):
        self.assertEqual(parse_program("(< 1 2)"), ConditionStatement(condition=BinaryComparison(comp_operator='<', first_condition_arg=ConditionArg(IntLiteral(1)), second_condition_arg=ConditionArg(IntLiteral(2)))))

    def test_condition_statement_binary_lessequal(self):
        self.assertEqual(parse_program("(<= 1 2)"), ConditionStatement(condition=BinaryComparison(comp_operator='<=', first_condition_arg=ConditionArg(IntLiteral(1)), second_condition_arg=ConditionArg(IntLiteral(2)))))

    def test_condition_statement_binary_more(self):
        self.assertEqual(parse_program("(>= 1 2)"), ConditionStatement(condition=BinaryComparison(comp_operator='>=', first_condition_arg=ConditionArg(IntLiteral(1)), second_condition_arg=ConditionArg(IntLiteral(2)))))

    def test_condition_statement_binary_moreequal(self):
        self.assertEqual(parse_program("(> 1 2)"), ConditionStatement(condition=BinaryComparison(comp_operator='>', first_condition_arg=ConditionArg(IntLiteral(1)), second_condition_arg=ConditionArg(IntLiteral(2)))))

    def test_condition_statement_binary_equal(self):
        self.assertEqual(parse_program("(== 1 2)"), ConditionStatement(condition=BinaryComparison(comp_operator='==', first_condition_arg=ConditionArg(IntLiteral(1)), second_condition_arg=ConditionArg(IntLiteral(2)))))

    def test_condition_statement_binary_notequal(self):
        self.assertEqual(parse_program("(!= 1 2)"), ConditionStatement(condition=BinaryComparison(comp_operator='!=', first_condition_arg=ConditionArg(IntLiteral(1)), second_condition_arg=ConditionArg(IntLiteral(2)))))

    def test_fun_def_statement_void_without_args_without_return(self):
        self.assertEqual(parse_program("(fun fn nil {})"), FunDefStatement(fun_identifier="fn", return_type=TokenType.T_NIL, args=[], fun_block=FunBlock([])))

    def test_fun_def_statement_void_without_args_with_void_return(self):
        self.assertEqual(parse_program("(fun fn nil {(ret nil)})"), FunDefStatement(fun_identifier="fn", return_type=TokenType.T_NIL, args=[], fun_block=FunBlock([ReturnStatement(return_arg=Void())])))

    def test_fun_def_statement_void_without_args_with_nonvoid_return(self):
        self.assertEqual(parse_program("(fun fn nil {(ret 1)})"), FunDefStatement(fun_identifier="fn", return_type=TokenType.T_NIL, args=[], fun_block=FunBlock([ReturnStatement(return_arg=IntLiteral(1))])))

    def test_fun_def_statement_void_with_args(self):
        self.assertEqual(parse_program("(fun fn nil (int k) (rom r) {})"), FunDefStatement(fun_identifier="fn", return_type=TokenType.T_NIL, args=[FunDefArg(var_type=TokenType.T_INT, var_identifier='k'), FunDefArg(var_type=TokenType.T_ROM, var_identifier='r')], fun_block=FunBlock([])))

    def test_fun_def_statement_non_void_without_args(self):
        self.assertEqual(parse_program("(fun fn int {(ret 1)})"), FunDefStatement(fun_identifier="fn", return_type=TokenType.T_INT, args=[], fun_block=FunBlock([ReturnStatement(return_arg=IntLiteral(1))])))

    def test_fun_call_without_args(self):
        self.assertEqual(parse_program("(fun fn int {(ret 1)})(fn)"), FunCallStatement(fun_identifier="fn", fun_args=[]))

    def test_fun_call_with_args(self):
        self.assertEqual(parse_program("(fun fn int (int k) (rom r) {(ret 1)})(fn 1 vi)"), FunCallStatement(fun_identifier="fn", fun_args=[FunCallArg(fun_call_arg=IntLiteral(1)), FunCallArg(fun_call_arg=RomanLiteral("vi"))]))

    def test_var_assign_statement_fun_call(self):
        self.assertEqual(parse_program("(fun fn int {(ret 1)})(= a (fn))"), AssignmentStatement(var_identifier='a', var_value=FunCallStatement(fun_identifier="fn", fun_args=[])))

    def test_var_assign_statement_fun_arithm(self):
        self.assertEqual(parse_program("(= a (+ 1 2))"), AssignmentStatement(var_identifier='a', var_value=ArithmeticStatement(operator="+",  first_arithm_arg=ArithmeticArg(IntLiteral(1)), second_arithm_arg=ArithmeticArg(IntLiteral(2)))))

    def test_var_assign_statement_condition(self):
        self.assertEqual(parse_program("(= a (< 1 2))"), AssignmentStatement(var_identifier='a', var_value=ConditionStatement(condition=BinaryComparison(comp_operator='<', first_condition_arg=ConditionArg(IntLiteral(1)), second_condition_arg=ConditionArg(IntLiteral(2))))))

    def test_var_assign_statement_concat(self):
        self.assertEqual(parse_program("(= a (. 'a' 'b'))"), AssignmentStatement(var_identifier='a', var_value=ConcatStatement(first_concat_arg=ConcatArg(TextLiteral('a')), second_concat_arg=ConcatArg(TextLiteral('b')))))


    def test_output_statement_fun_call(self):
        self.assertEqual(parse_program("(fun fn int {(ret 1)})(write (fn))"), OutputStatement(output_arg=FunCallStatement(fun_identifier="fn", fun_args=[])))

    def test_output_statement_fun_arithm(self):
        self.assertEqual(parse_program("(write (+ 1 2))"), OutputStatement(output_arg=ArithmeticStatement(operator="+",  first_arithm_arg=ArithmeticArg(IntLiteral(1)), second_arithm_arg=ArithmeticArg(IntLiteral(2)))))

    def test_output_statement_condition(self):
        self.assertEqual(parse_program("(write (< 1 2))"), OutputStatement(output_arg=ConditionStatement(condition=BinaryComparison(comp_operator='<', first_condition_arg=ConditionArg(IntLiteral(1)), second_condition_arg=ConditionArg(IntLiteral(2))))))

    def test_output_statement_concat(self):
        self.assertEqual(parse_program("(write (. 'a' 'b'))"), OutputStatement(output_arg=ConcatStatement(first_concat_arg=ConcatArg(TextLiteral('a')), second_concat_arg=ConcatArg(TextLiteral('b')))))

    def test_arithm_statement_arithm(self):
        self.assertEqual(parse_program("(+ 1 (+ 1 2))"), ArithmeticStatement(operator="+",  first_arithm_arg=ArithmeticArg(IntLiteral(1)), second_arithm_arg=ArithmeticArg(ArithmeticStatement(operator="+", first_arithm_arg=ArithmeticArg(IntLiteral(1)), second_arithm_arg=ArithmeticArg(IntLiteral(2))))))

    def test_arithm_statement_arithm(self):
        self.assertEqual(parse_program("(+ 1 (< 1 2))"), ArithmeticStatement(operator="+",  first_arithm_arg=ArithmeticArg(IntLiteral(1)), second_arithm_arg=ArithmeticArg(ConditionStatement(condition=BinaryComparison(comp_operator="<", first_condition_arg=ConditionArg(IntLiteral(1)), second_condition_arg=ConditionArg(IntLiteral(2)))))))

    def test_arithm_statement_fun_call(self):
        self.assertEqual(parse_program("(fun fn int {(ret 1)})(+ 1 (fn))"), ArithmeticStatement(operator="+", first_arithm_arg=ArithmeticArg(IntLiteral(1)), second_arithm_arg=ArithmeticArg(FunCallStatement(fun_identifier="fn", fun_args=[]))))

    def test_wrong_roman_num_format_will_raise_error(self):
        with self.assertRaises(ParserError):
            parse_program("(rom n)(= n VX)") 

unittest.main()