import config

last_directions = None

def authorised_to_shup(source):
    return True

def what_to_say(source, text, nickname, private):
    return ["This is a list of messages. I only know how to say one thing"]