

def read_file(path):
    payload = ""
    with open(path, 'r') as f:
        payload = f.read()
    return payload
