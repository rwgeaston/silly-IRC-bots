#var now = new Date();
#
#var a = new Date
#a.setHours(10);
#a.setMinutes(30);
#
#var s = new Date;
#s.setHours(11);
#s.setMinutes(30);
#
#var e = new Date
#e.setHours(13);
#e.setMinutes(0);
#
#var m = new Date
#m.setHours(14);
#m.setMinutes(0);
#
#var current = now.getTime();
#var almostLunch = a.getTime();
#var startLunch = s.getTime();
#var endLunch = e.getTime();
#var missedLunch = m.getTime();
#
#
#if ((current > almostLunch) && (current < startLunch)) {
#    document.write('<h1 class="almost">Almost</h1>');
#}
#else if ((current > endLunch) && (current < missedLunch)) {
#    document.write('<h1 class="missed">Just missed it</h1>');
#}
#else if ((current < startLunch) || (current > endLunch)) {
#    document.write('<h1>No</h1>');
#}
#else {
#    document.write('<h1 class="yes">Yes</h1>');
#}

from time import localtime


def what_to_say(bot, source, text, private):
    if "lunchtime?" in text or "is it lunchtime yet?" in text:
        return ["{}: {}. See http://isitlunchtimeyet.com/.".format(source, get_is_lunchtime())]
    return []


def get_is_lunchtime():
    time_now = localtime()
    if ((time_now.tm_hour == 10 and time_now.tm_min >= 30) or
        (time_now.tm_hour == 11 and time_now.tm_min < 30)):
        return 'Almost'
    elif ((time_now.tm_hour == 11 and time_now.tm_min >= 30) or
          (time_now.tm_hour == 12)):
        return 'Yes'
    elif time_now.tm_hour == 13:
        return 'Just missed it'
    else:
        return 'No'


def authorised_to_shup(source, owner):
    return True