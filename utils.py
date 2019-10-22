"""
Some utility functions
"""

def read_file(path):
    """
    read whole file in one string
    """
    with open(path) as inp_file:
        return inp_file.read()
