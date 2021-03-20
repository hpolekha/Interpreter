class Variable:
    def __init__(self, var_type, identifier, value=None):
        self.var_type = var_type
        self.identifier = identifier
        self.value = value

class Function:
    def __init__(self, identifier, return_type, args, block):
        self.identifier = identifier
        self.return_type = return_type
        self.args = args
        self.block = block