#! /usr/bin/env python
# 
# based on a python libirc example by Joel Rosdahl <joel@rosdahl.net>

from generic_bot import TestBot
import googledirections_speech

class GoogleDirectionsBot(TestBot):
    def decide_what_to_say(self, source, text):
        return googledirections_speech.what_to_say(source, text, self.nickname)
    
    def reload_modules(self):
        reload(googledirections_speech)
