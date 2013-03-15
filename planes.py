#! /usr/bin/env python
# 
# based on a python libirc example by Joel Rosdahl <joel@rosdahl.net>

from generic_bot import TestBot
import planes_speech

class PlanesBot(TestBot):
    def __init__(self, channel, nickname, owner, server='irc.rd.tandberg.com', port=6667):
        TestBot.__init__(self, channel, nickname, owner, server, port)
        print "PlanesBot probably running now: %s %s" % (server, port)
        
    def decide_what_to_say(self, source, text):
        return planes_speech.what_to_say(source, text)
    
    def reload_modules(self):
        reload(planes_speech)
