import config
import googledirections
reload(googledirections)
from googledirections import GoogleDirections
from time import time, gmtime, mktime

usage_help = ('''Get directions from Google Maps.
usage examples:
from slough to ealing
cycle to slough tesco <- no "from" field specified so I'll assume %s
public transport to maidenhead leaving at 19:00
public transport to iver <- no time so I'll assume you're leaving now
public transport to staines arriving at 11:00
walk from uxbridge to windsor with alternatives <- will give choice of routes
cycle to high wycombe with distances/times/details <- will print extra information (choose one)''' %
config.my_address)

class ParseException(Exception):
    pass

last_directions = None

def what_to_say(source, text, my_nickname):
    global last_directions
    destination = text[7:].strip()
    if text.find("%s:" % my_nickname) == 0:
        request = text[len(my_nickname) + 1:].lower()
        if request.find("help") >= 0:
            return usage_help.split('\n')
        else:
            try:
                alternative_route_to_show = int(request)
                if last_directions:
                    if len(last_directions[0].directions['routes']) >= alternative_route_to_show:
                        return last_directions[0].list_steps(alternative_route_to_show,
                                                             last_directions[1])
                    else:
                        return ['I don\'t remember having that many alternative routes']
                else:
                    return ['I don\'t remember listing any alternatives']
            except ValueError:
                return new_route(request)
    return []

def new_route(request):
    global last_directions
    try:
        origin, destination, options, display_options = parse_directions_request(request)
    except ParseException as exception_message:
        return ["I couldn't work out what to do there: %s" % exception_message]
    print origin, destination, options
    directions = GoogleDirections(origin, destination, options)
    status = directions.directions['status']
    if status != 'OK':
        if status == 'ZERO_RESULTS':
            return ['I couldn\'t find a route']
        elif status == 'NOT_FOUND':
            return ['I couldn\'t make sense of one of the places you said',
                    origin, destination]
        else:
            return ['Something went wrong and I don\'t know what: %s' % status,
                    str(options)]
    else:
        if len(directions.directions['routes']) > 1:
            last_directions = (directions, display_options)
            return directions.summaries()
        else:
            return directions.list_steps(1, display_options)
                
def parse_directions_request(request):
    if len(request.split(' to ')) != 2:
        raise ParseException('Either you didn\'t say "to" or said it too much')
    for option in ['distance', 'times', 'details']:
        if ('with %s' % option) in request:
            display_option = option
            request = request.replace('with %s' % display_option, '')
            break
    else:
        display_option = 'none'
    options = {'sensor':'false', 'region':config.my_TLD, 'units':'imperial'}
    if 'with alternatives' in request:
        options.update({'alternatives':'true'})
        request = request.replace('with alternatives', '')
    for travel_method in [('cycle', 'bicycling'),
                          ('walk', 'walking'),
                          ('public transport', 'transit'),
                          ('transit', 'transit')]:
        if travel_method[0] in request:
            options.update({'mode':travel_method[1]})
            request = request.replace(travel_method[0], '')
    for time_requirement in [('arriving at', 'arrival_time'),
                             ('leaving at', 'departure_time')]:
        if time_requirement[0] in request:
            request, travel_time = request.split(time_requirement[0])
            current_time = gmtime(time())
            try:
                travel_hour, travel_minute = [int(thing) for thing in travel_time.split(':')]
            except ValueError:
                options.update({'departure_time':str(int(time()))})
            time_to_use = time()
            if ((current_time.tm_hour == travel_hour and (current_time.tm_min - 5) > travel_minute) or
               (current_time.tm_hour > travel_hour)):
                time_to_use += 60 * 60 * 24
            time_to_use += 60 * (60 * (travel_hour - current_time.tm_hour) +
                                 (travel_minute - current_time.tm_min))
            options.update({time_requirement[1]:int(time_to_use)})
            break
    else:
        options.update({'departure_time':str(int(time()))})

    origin, destination = request.split(' to ')
    destination = destination.strip()
    origin = origin.strip(' from ')
    origin = origin.strip()
    if len(origin) == 0:
        origin = config.my_address
    return origin, destination, options, display_option