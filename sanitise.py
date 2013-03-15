def ascii_me(string):
    return ''.join([ascii_me_character(char) for char in string])

def ascii_me_character(char):
    if ord(char) > 128:
        return '?'
    else:
        return char