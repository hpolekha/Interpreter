import os

class SourceString():

    def __init__(self, source_str):
        self.source_str = source_str

    def read_next_symbol(self):
        result = ""
        if len(self.source_str) > 0:
            result = self.source_str[0]
            self.source_str = self.source_str[1:]
        return result

class SourceFile():
    def __init__(self, source_file):
        self.source_file = source_file
        self.f = None
        if os.path.isfile(source_file):
            self.f = open(source_file, 'r')

    def read_next_symbol(self):
        result = ""
        if self.f and not self.f.closed:
            result = self.f.read(1)

        return result

    def __del__(self):
        if self.f:
            self.f.close()