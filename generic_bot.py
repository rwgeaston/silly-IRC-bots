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
from traceback import format_exc


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
        self.messenger_config = {'wait_time':0.75, 'message_everyone':True}
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

    def message(self, target, messages):
        for line in messages:
            if type(line) not in [str, unicode]:
                print "You can't message this!"
                print "I'm not even going to try."
                print messages
                break
        else:
            self.messenger.messenger.add_to_queue(target, messages)

    def public(self, messages):
        """Dangerous! Bit hacky to include this at all but I got the architecture all wrong"""
        self.message(self.channel, messages)

    def raw_message(self, target, message):
        message = message.strip()
        message = message.replace('\n', '')
        message = message.replace('\r', '')
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
                self.raw_message(self.owner, "halp reloading")
                self.message_broken(thisbroke)
        elif not self.broken:
            try:
                target, messages = bot_action_decision.actions(self, source, text, private)
            except Exception as thisbroke:
                self.raw_message(self.owner, 'halp')
                self.message_broken(thisbroke)
            else:
                if target:
                    self.message(target, messages)

    def message_broken(self, thisbroke):
        error = ("%s had an error of type %s: %s (in the decision thread)" %
                (self.nickname, type(thisbroke), thisbroke))
        print error
        self.message(self.owner, error.split('\n'))
        traceback = format_exc(thisbroke)
        print traceback
        self.message(self.owner, traceback.split('\n'))
        self.broken = True
