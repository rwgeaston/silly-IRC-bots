from urllib2 import urlopen
from lxml import etree

class FlightTimes(object):
    def __init__(self):
        self.update()
        
    def update(self):
        departures = urlopen('http://www.heathrowairport.com/flight-information/live-flight-departures')
        raw_page = ''.join([line for line in departures])
        
        start = raw_page.find('<table id="timeTable" summary="Flight Timetable search results">')
        end = raw_page.find('</table>')
        table = etree.XML(raw_page[start:end + 8]).getchildren()[0]
        
        flights = table.getchildren()
        keys = [thing.text.strip() for thing in flights[0]]
        self.flights_parsed = [dict(zip(keys,
                                         [thing.text.strip().replace('\n', ' ')\
                                         .replace('\t', '').replace('  ', ' ')
                           for thing in flight]))
                           for flight in flights[2:]]
        
    def get_flights(self, destination):
        print destination
        destination = destination.lower()
        results = {}
        error = False
        for flight in self.flights_parsed:
            try:
                if destination in flight['Departing to'].lower():
                    results.update({(flight['Sched. time'],
                                     flight['Terminal']):
                                     (flight['Flight number'],
                                      flight['Status'])})
            except KeyError as e:
                error = True
        if error:
            print 'not all listings could be parsed'
        return results
    
    def format(self, key, value):
        generic = "the %s from %s at %s" % (value[0],
                                        key[1],
                                        key[0].split(' ')[1][:-5])
        status = value[1].lower()
        if "airborne" in status:
            return "You just missed %s" % generic
        elif "delayed" in status:
            return "Take %s (%s)" % (generic, status)
        else:
            return "Take %s" % generic
    
    def get_formatted_flights(self, destination):
        times = self.get_flights(destination)
        return [self.format(flight, times[flight]) for flight in sorted(times.keys())]
