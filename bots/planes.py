#! /usr/bin/env python
# 
# based on a python libirc example by Joel Rosdahl <joel@rosdahl.net>

from generic_bot import TestBot
import planes_speech

class PlanesBot(TestBot):
    def decide_what_to_say(self, source, text):
        return planes_speech.what_to_say(source, text)
    
    def reload_modules(self):
        reload(planes_speech)
