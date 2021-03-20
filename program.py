from inode import *

class Program(INode):
    def __init__(self, statements):
        self.statements = statements

    def accept(self, visitor):
        visitor.visit(self)