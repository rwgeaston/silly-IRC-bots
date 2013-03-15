log = open("adventure_log.txt", 'a')
last_zorks = ['', '']

def what_to_say(source, text):
    global last_zorks
    global log
    if text.find("adventurer") >= 0 and text.find("?") >= 0:
        return ["I want to play zork!"]
    elif text.find("zork:") == 0:
        player_command = text[5:]
        if '' not in last_zorks:
            log.write('%s,%s,%s\n' % (player_command, last_zorks[0], last_zorks[1]))
    elif source == 'zork':
        last_zorks[0] = last_zorks[1]
        last_zorks[1] = text
    return []
    
