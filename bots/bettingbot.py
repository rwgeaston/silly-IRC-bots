#! /usr/bin/env python
# 
# based on a python libirc example by Joel Rosdahl <joel@rosdahl.net>

from generic_bot import TestBot
import bet_speech

class BettingBot(TestBot):
    def decide_what_to_say(self, source, text):
        return bet_speech.what_to_say(source, text, self.nickname)
    
    def reload_modules(self):
        reload(bet_speech)