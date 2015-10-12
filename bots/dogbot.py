import re

def authorised_to_shup(source, owner):
    return source == owner

dogged = ["No one"] * 2

def what_to_say(bot, source, request, private):
    global dogged
    match = re.match("dogbot: give (\w+) dog #?(1|2)", request)
    if match:
        which_dog = int(match.groups(0)[1]) - 1
        dogged[which_dog] = match.groups(0)[0]
        return [
            "{0} has dog #{1} http://crashreports.lal.cisco.com/reports/dog{1}.jpg."
            .format(dogged[which_dog], which_dog + 1)
        ]
    elif "who has the dog?" in request:
        return [
            "{1} has dog #{0} http://crashreports.lal.cisco.com/reports/dog{0}.jpg."
            .format(index + 1, recipient) for index, recipient in enumerate(dogged)
        ]
    match = re.match("who has dog #?(1|2)", request)
    if match:
        which_dog = int(match.groups(0)[0]) - 1
        return [
            "{1} has dog #{0} http://crashreports.lal.cisco.com/reports/dog{0}.jpg"
            .format(which_dog + 1, dogged[which_dog])
        ]
    return []
