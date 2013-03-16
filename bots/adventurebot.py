#! /usr/bin/env python
# 
# based on a python libirc example by Joel Rosdahl <joel@rosdahl.net>

from generic_bot import TestBot
import adventure_speech

class AdventureBot(TestBot):
    def decide_what_to_say(self, source, text):
        return adventure_speech.what_to_say(source, text)
    
    def reload_modules(self):
        reload(adventure_speech)
