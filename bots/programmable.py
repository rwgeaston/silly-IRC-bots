import re

phrases_filename = 'bots\learnt_phrases.txt'
phrases_file = open(phrases_filename, 'r')
phrases_raw = phrases_file.readlines()
phrases_file.close()

phrasebook = dict([phrase.strip().split('COMMAHERE') for phrase in phrases_raw])

phrases_file = open(phrases_filename, 'a')

waiting_for_new_phrases = {}
phrases_to_forget = {}

def authorised_to_shup(source, owner):
    return True

def what_to_say(bot, source, text, private):
    if source in waiting_for_new_phrases:
        new_phrases = waiting_for_new_phrases[source]
        new_phrases.append(text)
        if len(new_phrases) == 2:
            return learn_new_phrase(source, text)
    elif source in phrases_to_forget:
        return forget_phrase(source, text)
    elif text == "{}: new phrase".format(bot.nickname):
        waiting_for_new_phrases.update({source:[]})
    elif text == "{}: forget".format(bot.nickname):
        phrases_to_forget.update({source:True})
    else:
        messages = []
        for phrase in phrasebook:
            try:
                match = re.search(phrase,text)
            except:
                #assuming re exception
                match = re.search(re.escape(phrase),text)
            if match and phrasebook[phrase] != 'SILENCE':
                groups = match.groups()
                if groups:
                    try:
                        message = phrasebook[phrase] % groups
                        messages.append(message)
                    except:
                        pass
                else:
                    messages.append(phrasebook[phrase])

        return messages
    return []

def learn_new_phrase(source, text):
    trigger, response = waiting_for_new_phrases[source]
    del waiting_for_new_phrases[source]
    if len(trigger) < 4:
        return ["I'm not learning anything with a trigger that short!"]
    else:
        phrases_file.write('{trigger}COMMAHERE{response}\n'.format(trigger=trigger, response=response))
        phrasebook.update({trigger:response})
        return ['New phrase learnt! "{trigger}" -> "{response}"'.format(trigger=trigger, response=response)]
                       
def forget_phrase(source, text):
    phrases_file.write('{trigger}COMMAHERESILENCE\n'.format(trigger=text))
    phrasebook.update({text:'SILENCE'})
    del phrases_to_forget[source]
    return ['Will now not respond to: {trigger}'.format(trigger=text)]