"""
Some utility functions
"""

def read_file(path):
    """
    read whole file in one string
    """
    payload = ""
    with open(path, 'r') as inp_file:
        payload = inp_file.read()
    return payload
