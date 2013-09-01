from time import time, gmtime
from random import choice

def authorised_to_shup(source, owner):
    return True

def what_to_say(bot, source, text, private):
    if text.lower().startswith('hugbot: hug'):
        people = text[len('hugbot: hug'):].replace('me', source)
        return ["*hugs" + people + "*"]
    elif text.lower().startswith('hugbot: compliment '):
        people = text[len('hugbot: compliment'):]
        if ' me ' in people:
            return ["{}: You're nice, but a bit arrogant".format(source)]
        return ["You're the best," + people + "!"]
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
    elif 'hubot insult' in text or 'guppy: smack' in text or "hubot: insult" in text or 'guppy: slap' in text:
        if source not in ['route', 'rwge', 'hugbot', 'ships']:
            print 'kicking {}'.format(source)
            bot.connection.kick(bot.channel, source, "Less being mean; more hugging.")
    return []

def get_date(days_from_now):
    full_date = gmtime(time() + days_from_now * 24 * 3600)
    return "{}/{}".format(full_date.tm_mon, full_date.tm_mday)

pugs = ["http://i.imgur.com/MUaNdk2.jpg",
        "http://i.imgur.com/urK4kTp.jpg",
        "http://i.imgur.com/dkcXBGa.jpg"]