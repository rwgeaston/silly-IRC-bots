def ascii_me(string):
    return ''.join([ascii_me_character(char) for char in string])

def ascii_me_character(character):
    if len(character) != 1:
        print "What's this?: {}".format(character)
        return '?'
    elif ord(character) > 256:
        return '?'
    else:
        return character