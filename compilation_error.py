class CompilationError(Exception):

    def __init__(self, text, lineno=None):
        self.text = text
        self.lineno = lineno
