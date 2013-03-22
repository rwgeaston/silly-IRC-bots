#! /usr/bin/env python
# 
# based on srjbot
#
# based on a python libirc example by Joel Rosdahl <joel@rosdahl.net>

import irc.bot
from time import sleep
from sanitise import ascii_me
from messenger import Messenger
from threading import Thread
import bot_action_decision
    
class messenger_thread(Thread):
    def __init__(self, irc_connection):
        self.messenger = Messenger(irc_connection)
        Thread.__init__(self)
        
    def run(self):
        self.messenger.run_loop()

class Bot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, owner, server='irc.rd.tandberg.com', port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.nickname = nickname
        self.owner = owner
        self.broken = False
        self.talk = True
        self.messenger_config = {'wait_time':1, 'message_everyone':True}
        self.messenger = messenger_thread(self)
        self.messenger.daemon = True
        self.messenger.start()
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
            try:
                print '\n\n reloading decision module\n\n'
                reload(bot_action_decision)
                self.broken = False
            except Exception as thisbroke:
                self.message(self.owner, "halp reloading")
                print ("%s had an error of type %s: %s (in the reload action)" %
                       (self.nickname, type(thisbroke), thisbroke))
                self.broken = True
        elif not self.broken:
            try:
                target, messages = bot_action_decision.actions(self, source, text, private)
                print self.nickname, target, len(messages)
            except Exception as thisbroke:
                self.message(self.owner, "halp")
                print ("%s had an error of type %s: %s (in the decision thread)" %
                       (self.nickname, type(thisbroke), thisbroke))
                self.broken = True
            else:
                if target:
                    self.messenger.messenger.add_to_queue(target, messages)
                