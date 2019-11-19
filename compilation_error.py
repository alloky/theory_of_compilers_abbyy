from enum import Enum, auto

class CompilationError(Exception):

    def __init__(self, error_type, text, lineno=None):
        self.error_type = error_type
        self.text = text
        self.lineno = lineno


class ErrorType(Enum):
    dublicatedClass = auto()
    dublicatedVariable = auto()
    dublicatedMethod = auto()
    dublicatedParam = auto()

    invalidName = auto()

    cycleInheritance = auto()
    methodInBaseWithDifferentSignature = auto()
    variableOverloading = auto()
    
    classNotFound = auto()

