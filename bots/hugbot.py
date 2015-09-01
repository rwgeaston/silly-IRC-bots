from time import time, gmtime
from random import choice

def authorised_to_shup(source, owner):
    return True

def what_to_say(bot, source, text, private):
    if "calm down aa" in text:
        return ["aa: http://imgur.com/gallery/nKjttSb"]
    if text.lower().startswith('hugbot: hug'):
        people = text[len('hugbot: hug'):].replace('me', source)
        return ["*hugs" + people + "*"]
    elif text.lower().startswith('hugbot: compliment '):
        people = text[len('hugbot: compliment'):]
        if ' me ' in people or people.endswith(' me'):
            return ["{}: You're nice, but a bit arrogant".format(source)]
        return ["You're the best," + people + "!"]
    elif text.lower().startswith('hugbot: when is hugging time?'):
        return ["Always!"]
    elif text.lower().startswith('hugbot: what is hometime?'):
        return ["Hometime is hugging time!"]
    elif text.lower().startswith('hugbot: forecast for '):
        place = text[len('hugbot: forecast for '):]
        dates = [get_date(days_from_now) for days_from_now in xrange(3)]
        return ["Forecast for {}".format(place)] + \
               ["{} - High of hugging, low of hugging. 95% chance of hugging.".format(date) for date in dates]
    elif "hugs hugbot" in text.lower():
        return ["\o/"]
    elif text.lower().startswith('hugbot: pug '):
        people = text[len('hugbot: pug'):].replace(' me', ' {}'.format(source))
        return ["{}: {}".format(people, choice(pugs)).strip()]
    elif private and source in ['littlerob', 'tjw'] and text.startswith('kick '):
        if text[5:] in ['rwge', 'hugbot']:
            return ["I won't kick them"]
        else:
            bot.connection.kick(bot.channel, text[5:], "Less being mean; more hugging.")
    bad_phrases = ['hubot insult', ': smack', "hubot: insult", ': slap', ': hit']
    if "*hugs " in text.lower():
        hug_target = text.split("*hugs ")[1]
        if "*" not in hug_target:
            return ["*hugs {}*".format(source)]
        else:
            return ["*hugs {} and {}*".format(source, hug_target.split("*")[0])]
    for phrase in bad_phrases:
        if phrase in text:
            if source not in ['route', 'rwge', 'hugbot', 'ships']:
                print 'kicking {}'.format(source)
                bot.connection.kick(bot.channel, source, "Less being mean; more hugging.")
    if source == 'guppy':
        print 'kicking {}'.format(source)
        bot.connection.kick(bot.channel, source, "Less being mean; more hugging.")
    if "It's just MARIO KART!" in text:
        if source not in ['route', 'rwge', 'hugbot', 'ships']:
            print 'kicking {}'.format(source)
            bot.connection.kick(bot.channel, source, "It's really not. It's just RUBBISH!")
    return []

def get_date(days_from_now):
    full_date = gmtime(time() + days_from_now * 24 * 3600)
    return "{}/{}".format(full_date.tm_mon, full_date.tm_mday)

pugs = [
    "http://i.imgur.com/MUaNdk2.jpg",
    "http://i.imgur.com/urK4kTp.jpg",
    "http://i.imgur.com/dkcXBGa.jpg",
    "http://i.imgur.com/XxpF9DG.jpg",
    "http://i.imgur.com/GRzT7J2.jpg",
    "http://i.imgur.com/guTeJxY.jpg",
    "http://i.imgur.com/ohkKyXx.jpg",
    "http://imgur.com/gallery/nKjttSb",
    "http://imgur.com/gallery/nKjttSb",
    "http://imgur.com/gallery/nKjttSb",
]
