###########################################################################
##
## Copyright (C) 2010 CSIR Meraka Institute. All rights reserved.
##
## eo4vistrails extends VisTrails, providing GIS/Earth Observation
## ingestion, pre-processing, transformation, analytic and visualisation
## capabilities . Included is the abilty to run code transparently in
## OpenNebula cloud environments. There are various software
## dependencies, but all are FOSS.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of VisTrails), please contact us at vistrails@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
"""This package provides general purpose date and time utility routines for
eo4vistrails.
"""

# library
from datetime import datetime, tzinfo, timedelta
import re
# thirdparty
from matplotlib import dates
from numpy import array, ma

ZERO = timedelta(0)
HOUR = timedelta(hours=1)


class FixedOffset(tzinfo):
    """Fixed offset in minutes east from UTC.

    Source:
        http://docs.python.org/library/datetime.html
    """

    def __init__(self, offset, name):
        self.__offset = offset  # timedelta(minutes = offset)
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO


def to_matplotlib_date(string, date_format='%Y-%m-%d', missing=1e-10):
    """Return a matplotlib date from a string, in the specified format,
    or 'almost zero' if invalid.

    Notes:
     *  Ignores time-zone settings appended with a +  or T because
        datetime.strptime cannot process those "as is".
    """
    if string:
        """
        string = str(string)
        # remove time zone
        if '+' in string:
            dt = string.split('+')
            _date = dt[0]
        elif 'Z' in string:
            dt = string.split('Z')
            _date = dt[0]
        else:
            _date = string
        # change separators to defaults
        if 'T' in _date:
            _date = _date.replace('T', ' ')
        if '/' in _date:
            _date = _date.replace('/', '-')

        try:
            return dates.date2num(datetime.strptime(_date, date_format))
        except ValueError, e:
            raise ValueError(e)
        """
        return dates.date2num(parse_datetime(string))
    return missing


def get_date_and_time(datetime_string, date_format="%Y-%m-%d",
                      time_format="%H:%M:%S"):
    """Return a tuple of date & time string values from a UTC-encoded date.

    Takes a string in the form YYYY-MM-DDTHH:MM:SSZaaaa and returns
    the date and time components as separate string values, formatted
    as specified by `date_format` and `time_format` respectively.
    """
    date = time = None
    if datetime_string:
        _dt = datetime_string.replace('T', ' ')
        if datetime_string[len(datetime_string) - 1] == 'Z':
            _dt = _dt.replace('Z', '')
        else:
            _dt = _dt.replace('Z', '+')
        _dt_python = parse_datetime(_dt)
        return (_dt_python.strftime(date_format),
               _dt_python.strftime(time_format))


def parse_datetime(string):
    """Create datetime object from string version of a date/time.

    Takes a string in a common date/time format, e.g. produced by calling str()
    on a Python datetime object or from an OGC web service, and returns a
    standard datetime instance.

    Acceptable formats are: "YYYY-MM-DD HH:MM:SS.ssssss+HH:MM",
                            "YYYY-MM-DD HH:MM:SS.ssssss",
                            "YYYY-MM-DD HH:MM:SS+HH:MM",
                            "YYYY-MM-DD HH:MM:SS"
    where ssssss represents fractional seconds.

    Alternative formats may use a 'T' as a separator between date and time.

    The timezone is optional and may be either positive or negative
    hours/minutes east of UTC.  The timezone may omit the ':' separator.

    Source:
        http://kbyanc.blogspot.com/2007/09/python-reconstructing-datetimes-from
        .html
    """
    # Pre-checks on string data
    if string is None:
        return None
    else:
        string = str(string)
    # convert UTC- into Python format
    if 'T' in string:
        string = string.replace('T', ' ')
    if 'Z' in string:
        if string[len(string) - 1] == 'Z':  # no time-zone info
            string = string.replace('Z', '')
        else:
            string = string.replace('Z', '+')
    # standard separators
    if '/' in string:
        string = string.replace('/', '-')

    # Split string in the form 2007-06-18 19:39:25.3300-07:00
    # into its constituent date/time, microseconds, and
    # timezone fields where microseconds and timezone are
    # optional.

    # some timezone fields omit the ':'
    if re.search(r'([-+]\d{4})', string):
        m = re.match(r'(.*?)(?:\.(\d+))?(([-+]\d{4}))?$', string)
        datestr, fractional, tzname, tz = m.groups()
        #print "datetimeutils:153", tz
        tz_field = re.findall(r'([-+]\d{4})', string)[0]
        #print "datetimeutils:153", tz_field
        tzhour = tz_field[1:3]
        tzmin = tz_field[3:5]
    else:
        m = re.match(r'(.*?)(?:\.(\d+))?(([-+]\d{1,2}):(\d{2}))?$', string)
        datestr, fractional, tzname, tzhour, tzmin = m.groups()
    #print "dtu:167", datestr, '*', tzname, '*', tzhour, '*', tzmin

    # Create tzinfo object representing the timezone
    # expressed in the input string.  The names we give
    # for the timezones are lame: they are just the offset
    # from UTC (as it appeared in the input string).  We
    # handle UTC specially since it is a very common case
    # and we know its name.
    if tzname is None:
        tz = None
    else:
        tzhour, tzmin = int(tzhour), int(tzmin)
        if tzhour == tzmin == 0:
            tzname = 'UTC'
        tz = FixedOffset(timedelta(hours=tzhour,
                                   minutes=tzmin), tzname)

    # Convert the date/time field into a python datetime
    # object.
    try:
        x = datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        x = datetime.strptime(datestr, "%Y-%m-%d")

    # Convert the fractional second portion into a count
    # of microseconds.
    if fractional is None:
        fractional = '0'
    fracpower = 6 - len(fractional)
    fractional = float(fractional) * (10 ** fracpower)

    # Return updated datetime object with microseconds and
    # timezone information.
    return x.replace(microsecond=int(fractional), tzinfo=tz)


def list_to_dates(items, date_format='%Y-%m-%d', missing=1e-10):
    """Convert a list into a list of masked date values, with each date
    in the specified date format.
    """
    #print "dtu:211", items
    if not items:
        return None
    x_data = [to_matplotlib_date(x, date_format) for x in items]
    return ma.masked_values(x_data, missing)  # ignore missing data
