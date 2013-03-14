#! /usr/bin/env python
# 
# based on a python libirc example by Joel Rosdahl <joel@rosdahl.net>

import time
from heathrow_scraper import FlightTimes
from generic_bot import TestBot

class PlanesBot(TestBot):
    def __init__(self, channel, nickname, server='irc.rd.tandberg.com', port=6667):
        TestBot.__init__(self, channel, nickname, server='irc.rd.tandberg.com', port=6667)
        self.flight_checker = FlightTimes()
        self.last_updated = time.time()
        
    def check_and_answer(self, e, text):
        c = self.connection
        source = e.source.nick
        if text.find("planes:") == 0 and "trains" not in source:
            if text.find("help") >= 0:
                self.message("Just say planes: <destination>")
            else:
                destination = text[7:].strip()
                if time.time() - self.last_updated > 5 * 60:
                    self.flight_checker.update()
                    self.last_updated = time.time()
                    print 'Updating'
                options = self.flight_checker.get_formatted_flights(destination)
                if len(options) == 0:
                    self.message("I can't find any flights to %s." % destination)
                    self.message("Trains: %s" % destination)
                else:
                    for flight in options:
                        self.message(flight)

def main():
    channel = '#test'
    nickname = 'planes'
    bot = PlanesBot(channel, nickname)
    bot.start()

if __name__ == "__main__":
    main()