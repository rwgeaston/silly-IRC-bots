def authorised_to_shup(source, owner):
    if owner:
        return True
    else:
        return False

def what_to_say(bot, source, request, private):
    return ["This is a list of messages. I only know how to say one thing"]