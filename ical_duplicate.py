from AppKit import NSPasteboard, NSString
from appscript import app, its, k
from osax import OSAX
# see http://appscript.sourceforge.net/py-appscript/doc/osax-manual/04_notes.html
import standardadditions
import re, sys
import datetime

def parse_date_time(date, time):
    return datetime.datetime.strptime('%s %s' % (date, time),
                                      '%B %d, %Y %I:%M %p')

def run():
    iCal = app(id='com.apple.iCal')

    iCal.activate()
    app(id='com.apple.systemevents').keystroke('c', using=k.command_down)

    eventString = NSPasteboard.generalPasteboard().readObjectsForClasses_options_(
        [NSString], {})[0]

    calendar_names = iCal.calendars[its.writable == True].name.get()

    sa = OSAX(id='com.apple.iCal', terms=standardadditions)
    calendar_name = sa.choose_from_list(calendar_names, with_title='Duplicate',
                                        with_prompt="Copy event to calendar:",
                                        default_items=[calendar_names[0]],
                                        OK_button_name="Duplicate",
                                        multiple_selections_allowed=False,
                                        empty_selection_allowed=False)
    if not calendar_name:
        sys.exit(0)
    calendar_name = calendar_name[0]

    p = {}

    p[k.summary], dates, other = eventString.split('\n', 2)

    date, start, end = re.match(r'scheduled (.+) from (.+) to (.+)',
                                dates).groups()
    p[k.start_date] = parse_date_time(date, start)
    p[k.end_date] = parse_date_time(date, end)

    if other.startswith('Location: '):
        location, p[k.description] = other.split('\n', 1)
        p[k.location] = location.split(': ', 1)[1]
    else:
        p[k.description] = other

    event = iCal.calendars[calendar_name].make(new=k.event, with_properties=p)
    event.make(new=k.sound_alarm, with_properties={
            k.trigger_interval: -10, k.sound_name: 'Basso'})
