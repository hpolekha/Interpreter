import re
from env_elements import *
from my_token import TokenType
from limits import *
from errors import *

class Enviroment:
    def __init__(self, visitor):
        self.global_functions = {}
        # at least one call context always exists
        # there are no global variables
        self.call_contexts = [CallContext()]
        self.last_result = None
        self.last_result_is_roman = False
        self.visitor = visitor

    def get_last_result(self):
        return self.last_result

    def set_last_result(self, result):
        self.last_result = result

    def create_call_context(self):
        self.call_contexts.append(CallContext())
    
    def delete_call_context(self):
        if self.call_contexts:
            self.call_contexts.pop()

    def create_block_context(self):
        # creating block context without call_contextare not allowed
        # creating block context in the last craeted call context
        if self.call_contexts:
            self.call_contexts[-1].create_block_context()

    def delete_block_context(self):
        # creating block context without call_contextare not allowed
        # delete block context from the last craeted call context
        if self.call_contexts:
            self.call_contexts[-1].delete_block_context()

    def get_var(self, name):
        if self.call_contexts:
            # find var in the last call_context
            var = self.call_contexts[-1].get_var(name)
            if var:
                return var

        # if there is no var in the last created call context, raise error
        self.visitor.raise_error(msg=str(name) + " was not declare in this scope")

    def get_var_value(self, name):
        var = self.get_var(name)

        # access to variable before assignment value
        if var.value is None:
            print(var.identifier)
            self.visitor.raise_error(msg="Read value from variable before assignment: " + str(var.identifier))

        # set info about var being of rom type
        if var.var_type == TokenType.T_ROM:
            self.last_result_is_roman = True
        else:
            self.last_result_is_roman = False

        return var.value

    def create_var(self, var_type, identifier, value=None):
        # create var in last created context
        if self.call_contexts:
            self.call_contexts[-1].create_var(var_type, identifier, value, self.visitor)

    def set_var(self, identifier, value, allow_convert=False):
        if self.call_contexts:
            # set value of var from the last created call context
            # raise error if there is no var with that name
            if self.call_contexts[-1].set_var(identifier, value, self, allow_convert):
                return          
       
        self.visitor.raise_error(msg=str(identifier) + " was not declare in this scope")

    def create_fun(self, identifier, return_type, args, block):
        # check if fun with same name does not already exist
        if identifier in self.global_functions:
            self.visitor.raise_error(msg=str(identifier) + " already declared in this scope")
        else:
            # if does not, create fun definition
            self.global_functions[identifier] = Function(identifier=identifier, return_type=return_type, args=args, block=block)

    def get_fun(self, identifier):
        # find obj represanting fun with this identifier
        if identifier in self.global_functions:
            return self.global_functions[identifier]
        # if there is no such obj, raise error
        else:
            self.visitor.raise_error(msg=str(identifier) + " was not declare in this scope")
    
    # raise error if value can not be write into var with var_type
    # if allow_convert is True, then also try to convert string to var_type
    #   it neccessary when reading from user terminal to num vars
    # value for rom num is istance of int, by self.last_result_is_roman differ int and rom
    # allow write:
    #  rom->int
    #  rom->real, int->real
    def parse_value_to(self, value, var_type, allow_convert=False):
        if var_type == TokenType.T_INT:
            # allow write rom into int
            # if value not a integer number
            if not isinstance(value, int):
                # if allow_convert then try to build int value by casting
                #  raise eror if not or if unsuccessfully
                if allow_convert:
                    try:
                        self.last_result = int(value)
                    except:
                        try:
                            self.last_result = self.roman_text_to_num(value)
                        except:
                            self.visitor.raise_error(msg="Invalid conversion to int: " + str(value))
                else:
                    self.visitor.raise_error(msg="Invalid conversion to int: " + str(value))
            else:
                self.last_result = value
            self.last_result_is_roman = False
            
            # raise error wnen max int limit was exceeded when writing value to var 
            if abs(self.last_result) > MAX_INT_ABSOLUTE_VALUE:
                self.visitor.raise_error(msg="Max int absolute value was exceeded")

        elif var_type == TokenType.T_REAL:
            # allow write rom and int into real
            # if value not number a type(int, float):
            if not isinstance(value, float) and not isinstance(value, int):
                # if allow_convert then try to build float value by casting
                #  raise eror if not or if unsuccessfully
                if allow_convert:
                    try:
                        self.last_result = float(value)
                    except:
                        try:
                            self.last_result = self.roman_text_to_num(value)
                        except:
                            self.visitor.raise_error(msg="Invalid conversion to real: " + str(value))
                else:
                    self.visitor.raise_error(msg="Invalid conversion to real: " + str(value))
            else:
                self.last_result = float(value)
            self.last_result_is_roman = False
            
            # raise error wnen max limit = max int limit was exceeded when writing value to var 
            if abs(self.last_result) > MAX_INT_ABSOLUTE_VALUE:
                self.visitor.raise_error(msg="Max real absolute value was exceeded")

        elif var_type == TokenType.T_ROM:
            # do not allow write int into roman
            # value is rom if its primitive type is int and self.last_result_is_roman is set to True
            if not isinstance(value, int) or not self.last_result_is_roman:
                # if value not rom try to build rom from value if allow_convert=True
                #  raise eror if not or if unsuccessfully
                if allow_convert:
                    try:
                        self.last_result = self.roman_text_to_num(value)
                    except:
                        self.visitor.raise_error(msg="Invalid conversion to rom: " + str(value))
                else:
                    self.visitor.raise_error(msg="Invalid conversion to rom: " + str(value))
            else:
                self.last_result = value
            self.last_result_is_roman = True

            # raise error wnen max rom limit was exceeded when writing value to var 
            if abs(self.last_result) > MAX_ROMAN_ABSOLUTE_VALUE:
                self.visitor.raise_error(msg="Max rom absolute value was exceeded")

        elif var_type == TokenType.T_TXT:
            # if value not string try to build string from value or raise error if allow_convert=False
            if not isinstance(value, str):
                if allow_convert:
                    self.last_result = str(value)
                else:
                    self.visitor.raise_error(msg="Invalid conversion to txt: " + str(value))
            else:
                self.last_result = value
            self.last_result_is_roman = False
            
            # raise error wnen max text length was exceeded when writing value to var 
            if len(self.last_result) > MAX_LENGTH_OF_STRING:
                self.visitor.raise_error(msg="Max length of txt varibale was exceeded")

        elif var_type == TokenType.T_NIL:
            self.last_result = None
            self.last_result_is_roman = False
            # self.visitor.raise_error(msg="Invalid conversion to nil: " + str(value))
            

        else:
            self.visitor.raise_error(msg="Undefined type casting")

    def roman_text_to_num(self, value):
        # check if rom string is in correct format
        # regex for max 9999 number
        # row and col will be overwritten by parser
        # make sure to work with string
        value = str(value).upper()
        if not value:
            self.visitor.raise_error(msg="Invalid conversion to rom: " + str(value))
        if not re.search(r"^(-)?M{0,9}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", value):
            self.visitor.raise_error(msg="Invalid conversion to rom: " + str(value))
        
        # remember about minus at the begining of negative rom number
        # but remove it for calculating absolute rom value
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

        # if there was minus symbol at the begining, make rom num negative
        if is_negative:
            int_value *= -1

        return int_value

        

class CallContext:
    def __init__(self):
        # there is at least one block context in each call context
        self.block_contexts = [BlockContext()]

    def get_var(self, name):
        # start searching var from the last created block context
        # and move to the older ones
        for block_context in reversed(self.block_contexts):
            var = block_context.get_var(name)
            if var:
                return var
        return None
    
    def set_var(self, identifier, value, env, allow_convert):
        # start searching var from the last created block context
        # and move to the older ones
        for block_context in reversed(self.block_contexts):
            if block_context.set_var(identifier, value, env, allow_convert):
                return True
        return False

    def create_var(self, var_type, identifier, value, visitor):
        # create/define var in the last created block context
        self.block_contexts[-1].create_var(var_type, identifier, value, visitor)

    def create_block_context(self):
        self.block_contexts.append(BlockContext())

    def delete_block_context(self):
        # remove last created block context
        if self.block_contexts:
            self.block_contexts.pop()

class BlockContext:
    def __init__(self):
        self.local_vars = {}

    def get_var(self, name):
        if name in self.local_vars:
            return self.local_vars[name]
        return None 

    def set_var(self, identifier,  value, env, allow_convert):
        if identifier in self.local_vars:
            # raise error if cannot write value into var with inproperate var_type
            env.parse_value_to(value, self.local_vars[identifier].var_type, allow_convert)
            self.local_vars[identifier].value = env.get_last_result()
            return True
        return False

    def create_var(self, var_type, identifier, value, visitor):
        # raise error if already existss with the same name, create var otherwise
        if identifier in self.local_vars:
            visitor.raise_error(msg=str(identifier) + " already declared in this scope")
        else:
            self.local_vars[identifier] = Variable(var_type, identifier, value)