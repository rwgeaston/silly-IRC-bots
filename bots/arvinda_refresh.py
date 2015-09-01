source_url = ["http://dt8b5.test.lal.cisco.com/endpoint_rx_preview.jpeg?guid=6f088e90-d789-11e3-b640-000d7c10cc60&key=be862710-d118-11e3-b63f-000d7c10cc60&size=large"]
talk = False

def authorised_to_shup(source, owner):
    return True

def what_to_say(bot, source, request, private):
    global talk
    global source_url
    if not request.startswith(bot.nickname + ": "):
        return []

    request = request[len(bot.nickname) + 2:]
    if request.startswith('source: '):
        print "new source: " + request[len('source: '):]
        source_url[0] = request[len('source: '):]
    elif request == 'start':
        talk = True
        bot.message("picture", source_url)
    elif request == 'stop':
        talk = False
    elif request == 'source?':
        return source_url
    elif source == 'picture' and "I think I've uploaded it" in request and talk:
        bot.message("picture", source_url)
    return []
