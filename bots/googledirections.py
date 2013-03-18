from urllib2 import build_opener
from ast import literal_eval
from sanitise import ascii_me

google_opener = build_opener()
google_opener.addheaders = [('User-agent', 'Mozilla/5.0')]

class GoogleDirections(object):
    def __init__(self, origin, destination, options = None):
        """Get directions from Google API giving origin and destination
        
        likely options:
        mode can be driving, walking, transit, bicycling
        avoid can be tolls or highways
        region e.g. uk, based on country TLD
        departure_time or arrival_time in seconds"""
        if not options:
            options = {'sensor':'false'}
        options.update({'origin':origin, 'destination':destination})
        baseurl = "http://maps.googleapis.com/maps/api/directions/json?"
        get = '&'.join(["%s=%s" % (option, options[option]) for option in options])
        fullurl = (baseurl + get).replace(' ', '%20')
        print fullurl
        raw = google_opener.open(fullurl)
        self.directions = literal_eval(raw.read())

    def list_steps(self, route=1, display_options=None):
        """Readable version of the route steps
        
        display_options = 'distance'/'times'/'details'/None
        gives most detailed printout"""
        steps_clean = [" -- %s" % no_html(
                      self.directions['routes'][route - 1]['legs'][0]['start_address'])]
        for leg in self.directions['routes'][route - 1]['legs']:
            for step in leg['steps']:
                raw = step['html_instructions']
                clean = no_html(raw)
                time = time_format(step['duration']['text'])
                distance = step['distance']['text']
                if display_options in ['distance', 'details']:
                    clean = "%s | %s" % (distance, clean)
                if display_options in ['times', 'details']:
                    clean = "%s | %s" % (time, clean)
                if 'transit_details' in step:
                    clean = ('%s (%s, departure time: %s)' %
                            (clean,
                             step['transit_details']['line']['name'],
                             step['transit_details']['departure_time']['text']))
                steps_clean.append(clean)
                if 'transit_details' in step:
                    transit_companies = step['transit_details']['line']['agencies']
                    for company in transit_companies:
                        steps_clean.append('(%s | %s)' % (company['name'], company['url']))
                    steps_clean.append("Get off at %s" % step['transit_details']['arrival_stop']['name'])
                    
            steps_clean.append(" -- %s" % no_html(leg['end_address']))
        copyright = self.directions['routes'][route - 1]['copyrights']
        steps_clean.append(copyright.replace('\xc2\xa9', 'c'))
        return steps_clean
    
    def summaries(self):
        summaries = []
        for index, route in enumerate(self.directions['routes']):
            total_distance = 0
            total_time = 0
            for leg in route['legs']:
                total_distance += leg['distance']['value']
                total_time += leg['duration']['value']
            miles = total_distance / 1609.344
            minutes = (total_time / 60) % 60
            hours = total_time / 3600
            if 'summary' in route:
                summary = route['summary']
            else:
                summary = [] 
                for leg in route['legs']:
                    for step in leg['steps']:
                        if step['travel_mode'] == 'TRANSIT':
                            summary.append(step['transit_details']['line']['vehicle']['name'])
                if len(summary) == 0:
                    summary = ['Walk']
                summary = '/'.join(summary)
            summaries.append("%s %s | %.2f miles | %sh%s" % (index + 1, summary, miles, hours, minutes))
        return summaries

def time_format(time_string):
    if 'hour' in time_string:
        return time_string.replace(' hour ', ':').strip(' minutes')
    else:
        return time_string

def no_html(string):
    # get rid of some html crud
    return (string.replace('\u003cb\u003e', '')
                  .replace('\u003c/b\u003e', '')
                  .split('\u003cdiv')[0])
