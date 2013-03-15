from time import sleep
from threading import Thread

from planes import PlanesBot
from lowestoddsbot import LowestOddsBot
from adventurebot import AdventureBot

channel = '#test'
server = 'irc.rd.tandberg.com'
owner = 'littlerob'

class run_bot(Thread):
    def __init__(self, *args):
        self.args = args
        Thread.__init__(self)
        
    def run(self):
        bot = self.args[0](*(self.args[1:]))
        bot.start()

bot_map = {'planes':PlanesBot, 'drybones':LowestOddsBot, 'adventurer':AdventureBot}
        
bot_threads = {}

for nickname in ['planes', 'adventurer']:
    bot_class = bot_map[nickname]
    print bot_class, nickname
    bot_threads.update({nickname:run_bot(bot_class,
                                         channel,
                                         nickname,
                                         owner,
                                         server)})
    print 'created %s' % nickname
    bot_threads[nickname].daemon = True
    bot_threads[nickname].start()
    sleep(5)

print 'everyone should be running'

while True:
    sleep(1)