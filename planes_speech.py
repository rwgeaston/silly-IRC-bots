from time import time
from heathrow_scraper import FlightTimes

flight_checker = FlightTimes()
last_updated = time()

def what_to_say(source, text):
    global last_updated
    if text.find("planes:") == 0 and "trains" not in source:
        if text.find("help") >= 0:
            return ["Just say planes: <destination>"]
        elif len(text) > 2:
            destination = text[7:].strip()
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