last_zorks = ['', '']

def what_to_say(source, text):
    global last_zorks
    if text.find("adventure") >= 0 and text.find("?") >= 0:
        return ["I want to play zork!"]
    elif text.find("zork:") == 0:
        player_command = text[5:]
        print player_command, last_zorks
        if '' not in last_zorks:
            log = open("adventure_log.txt", 'a')
            log.write('%sSPLITME%sSPLITME%s\n' % (player_command, last_zorks[0], last_zorks[1]))
            log.close()
    elif source == 'zork':
        last_zorks[0] = last_zorks[1]
        last_zorks[1] = text
    return []
    
