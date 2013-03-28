from bots import botmap_config
reload(botmap_config)

def actions(bot, source, text, private):
    messages = []
    decision_module = botmap_config.bot_map[bot.nickname]
    if bot.nickname in text and ("shup" in text or ('shut' in text and 'up' in text)):
        if private:
            bot.messenger.messenger.wipe(source)
            messages = ["ok... :("]
        elif decision_module.authorised_to_shup(source, bot.owner):
            bot.messenger.messenger.wipe(bot.channel)
            messages = ["ok... :("]
    else:
        messages = decision_module.what_to_say(bot, source, text, private)
    if private:
        return source, messages
    else:
        if len(messages) > 50:
            bot.messenger.messenger.add_to_queue(
                                bot.channel,
                                ["{0}: This is too much to say here so I'll PM you...".format(source)])
            return source, messages
        return bot.channel, messages