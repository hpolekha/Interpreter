import sys
import os
from lexer import *
from parser import *
from interpreter import *
from source import *

if len(sys.argv) < 2:
    print('Input file name.')
else:
    if os.path.isfile(sys.argv[1]):
        lexer = Lexer(SourceFile(sys.argv[1]))
        try: 
            parser = Parser(lexer)      
            program = parser.parse_program()
            interpreter = Interpreter(program)
            interpreter.execute()
        except OwnError as ex:
            print(ex)
    else:
        print("Can not open file.")

        

