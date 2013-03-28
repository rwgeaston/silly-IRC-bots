from Queue import Queue
from time import sleep
from sanitise import ascii_me
from threading import Lock

class Messenger(object):
    def __init__(self, irc_connection):
        self.message = irc_connection.message
        self.irc_connection = irc_connection
        self.lock = Lock()
        self.message_queues = []
        self.queue_to_check = 0
        
    def run_loop(self):
        while True:
            sleep(self.irc_connection.messenger_config['wait_time'])
            if self.irc_connection.messenger_config['message_everyone']:
                with self.lock:
                    for index in reversed(xrange(len(self.message_queues))):
                        if self.message_queues[index][1].empty():
                            del(self.message_queues[index])
                    for target in self.message_queues:
                        if not target[1].empty():
                            self.send_message_with_exception_catch(target[0],
                                                                   target[1].get())
            else:
                target, message = self.find_message()
                self.send_message_with_exception_catch(target, message)
                
    def send_message_with_exception_catch(self, target, message):
        if message:
            try:
                self.message(target, ascii_me(message))
            except UnicodeDecodeError as error:
                print 'UnicodeDecodeError'
                print error
                print [message]
                raise
            except Exception as thisbroke:
                self.message(irc_connection.owner, "halp")
                print ("%s had an error of type %s: %s (in the messenger thread)" %
                       (self.nickname, type(thisbroke), thisbroke))
                self.broken = True
                
    def find_message(self):
        with self.lock:
            for index in reversed(xrange(len(self.message_queues))):
                if self.message_queues[index][1].empty():
                    del(self.message_queues[index])
            if len(self.message_queues) == 0:
                return None, None
            if self.queue_to_check == len(self.message_queues):
                self.queue_to_check = 0
            relevant_queue = self.message_queues[self.queue_to_check]
            message = relevant_queue[1].get()
            target = relevant_queue[0]
            self.queue_to_check += 1
            return target, message
        return None, None

    def add_to_queue(self, new_target, messages):
        with self.lock:
            for target in self.message_queues:
                if target[0] == new_target:
                    for message in messages:
                        target[1].put(message)
                    break
            else:
                self.message_queues.append([new_target, Queue()])
                for message in messages:
                    self.message_queues[-1][1].put(message)
                    
    def wipe(self, who_to_wipe = 'everyone!'):
        print 'wiping %s' % who_to_wipe
        with self.lock:
            for index, target in enumerate(self.message_queues):
                if who_to_wipe == 'everyone!' or who_to_wipe == target[0]:
                    del self.message_queues[index]
            print self.message_queues