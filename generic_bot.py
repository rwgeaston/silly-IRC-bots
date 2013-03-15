#! /usr/bin/env python
# 
# based on srjbot
#
# based on a python libirc example by Joel Rosdahl <joel@rosdahl.net>

import irc.bot
from time import sleep
from sanitise import ascii_me

class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, owner, server='irc.rd.tandberg.com', port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.nickname = nickname
        self.owner = owner
        self.broken = False
        print "%s probably running now: %s %s" % (nickname, server, port)

    def on_nicknameinuse(self, connection, event):
        connection.nick(connection.get_nickname() + "_")

    def on_welcome(self, connection, event):
        connection.join(self.channel)

    def on_pubmsg(self, connection, event):
        self.check_and_answer(event, False)
        return
    
    def on_privmsg(self, connection, event):
        self.check_and_answer(event, True)
        return
    
    def message(self, target, message):
        self.connection.privmsg(target, message)
        
    def check_and_answer(self, event, private):
        text = ascii_me(event.arguments[0])
        source = event.source.nick
        if (source == self.owner and text == "%s: feeling better?" % self.nickname):
            self.reload_modules()
            print '\n\n reloading %s\n\n' % self.nickname
            self.broken = False
        elif not self.broken:
            try:
                messages = self.decide_what_to_say(source, text)
            except Exception as thisbroke:
                self.message(self.owner, "halp")
                print self.nickname, thisbroke
                self.broken = True
                messages = []
            for count, message in enumerate(messages):
                sleep(min(1.5, 0.3 * count))
                if private:
                    self.message(source, message)
                else:
                    self.message(self.channel, message)