from time import time
from heathrow_scraper import FlightTimes

flight_checker = FlightTimes()
last_updated = time()

def what_to_say(source, text, nickname, private):
    global last_updated
    destination = text[7:].strip()
    if text.find("planes:") == 0 and "trains" not in source:
        if text.find("help") >= 0:
            return ["Just say planes: <destination>"]
        elif text.find("crash") >= 0:
            return ["I'm being flown by a bot. I can't crash any more!"]
        elif text.find("rwge") >= 0:
            return ["rwge is already here; you don't need to fly to him"]
        elif len(destination) > 2:
            if time() - last_updated > 5 * 60:
                flight_checker.update()
                last_updated = time()
                print 'Updating'
            options = flight_checker.get_formatted_flights(destination)
            if len(options) == 0:
                return ["I can't find any flights to %s." % destination,
                        "trains: %s" % destination]
            else:
                return options
    return []

def authorised_to_shup(source, owner):
    return True
