from time import sleep
from threading import Thread
import config
from generic_bot import Bot

class run_bot(Thread):
    def __init__(self, *args):
        self.args = args
        Thread.__init__(self)
        
    def run(self):
        self.bot = self.args[0](*(self.args[1:]))
        self.bot.start()
        
    def stop_bot(self):
        self.bot.disconnect()
        self.bot.connection.close()
        
    def talking(self, whether_to_talk):
        self.bot.talk = whether_to_talk

bot_threads = {}

def start(nickname):
    bot_threads.update({nickname:run_bot(Bot,
                                         config.channel,
                                         nickname,
                                         config.owner,
                                         config.server)})
    print 'created %s' % nickname
    bot_threads[nickname].daemon = True
    bot_threads[nickname].start()
    
def stop(nickname):
    bot_threads[nickname].stop_bot()
    bot_threads[nickname]._Thread__stop()

def wipe():
    for nickname in bot_threads:
        bot_threads[nickname].bot.messenger.messenger.wipe()