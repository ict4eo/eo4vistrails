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
EO4VisTrails.
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
        `<http://docs.python.org/library/datetime.html>`_
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


def list_to_dates(items, date_format='%Y-%m-%d', missing=1e-10):
    """Convert a list into a list of masked date values, with each date
    in the specified date format.
    """
    #print "dtu:66", items
    if not items:
        return None
    x_data = [to_matplotlib_date(x, date_format) for x in items]
    return ma.masked_values(x_data, missing)  # ignore missing data


def get_date(string, date_format='%Y-%m-%d', missing=1e-10):
    """Return a formatted date, or date/time, value from a string."""
    if string:
        _dt = parse_datetime(string)
        return _dt.strftime(date_format)
    else:
        return None


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


def to_matplotlib_date(string, missing=1e-10):
    """Return a matplotlib date from a string, or 'almost zero' if invalid.
    """
    if string:
        return dates.date2num(parse_datetime(string))
    return missing


def parse_datetime(string):
    """Create datetime object from string version of a date/time.
    
    Takes a string in a common date/time format, e.g. produced by calling str()
    on a Python datetime object or from an OGC web service, and returns a
    standard datetime instance.
    
    Acceptable formats are:
    *   "YYYY-MM-DD HH:MM:SS.sss+HHMM"
    *   "YYYY-MM-DD HH:MM:SS+HHMM"
    *   "YYYY-MM-DD HH:MM:SS+HH"
    *   "YYYY-MM-DD HH:MM:SS"
    where sss represents fractional seconds. The '-' may be replaced by a '/'.
    
    Alternative formats may use a 'T' as a separator between date and time.
    
    The timezone is optional and may be either positive or negative
    hours/minutes east of UTC.  The timezone should omit the ':' separator; if
    present it will be removed.
    
    Source:
        `<http://kbyanc.blogspot.com/2007/09/python-reconstructing-datetimes-from.html>`_
    
    .. code-block:: python
    
        assert parse_datetime('2012-08-09') == datetime(2012, 8, 9, 0, 0)
        assert parse_datetime('2012-08-09 12:12:23') == datetime(2012, 8, 9, 12, 12, 23)
        assert parse_datetime('2012-08-09 12:12:23.456') == datetime(2012, 8, 9, 12, 12, 23, 456000)
        # assert fails because tzinfo objects differ...
        assert parse_datetime('2012-08-09 12:12:23+02') == \
        datetime(2012, 8, 9, 12, 12, 23, tzinfo=FixedOffset(timedelta(hours=2),'UTC'))
        assert parse_datetime('2012-08-09 12:12:23.456+02') == \
        datetime(2012, 8, 9, 12, 12, 23, 456000, tzinfo=FixedOffset(timedelta(hours=2),'UTC'))
        assert parse_datetime('2012-08-09 12:12:23+0200') == \
        datetime(2012, 8, 9, 12, 12, 23, tzinfo=FixedOffset(timedelta(hours=2),'UTC'))
        assert parse_datetime('2012-08-09 12:12:23.456+02:30') == \
        datetime(2012, 8, 9, 12, 12, 23, 456000, tzinfo=FixedOffset(timedelta(hours=2, minutes=30),'UTC'))
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
    if '+' in string and string[-3:-2] == ':':
        string = '%s%s' % (string[:-3], string[-2:])
    # standard separators
    if '/' in string:
        string = string.replace('/', '-')
    #print "datetimeutils:167", string

    # Split string in the (general) form 2007-06-18 19:39:25.3300-0700
    # into its constituent date/time, microseconds, and timezone fields where
    # microseconds and timezone are optional.

    # check for HHMM timezone entry
    if len(string) > 10 and re.search(r'([-+]\d{4})', string):
        m = re.match(r'(.*?)(?:\.(\d+))?(([-+]\d{4}))?$', string)
        datestr, fractional, tzname, tz = m.groups()
        #print "datetimeutils:159", tz
        tz_field = re.findall(r'([-+]\d{4})', string)[0]
        #print "datetimeutils:181", tz_field
        tzhour = tz_field[1:3]
        tzmin = tz_field[3:5]
    # check for HH timezone entry
    elif len(string) > 10 and re.search(r'([-+]\d{2})', string):
        m = re.match(r'(.*?)(?:\.(\d+))?(([-+]\d{2}))?$', string)
        datestr, fractional, tzname, tz = m.groups()
        #print "datetimeutils:187", tz
        tz_field = re.findall(r'([-+]\d{2})', string)[0]
        #print "datetimeutils:189", tz_field
        tzhour = tz_field[1:3]
        tzmin = '00'
    else:
        m = re.match(r'(.*?)(?:\.(\d+))?(([-+]\d{1,2}):(\d{2}))?$', string)
        datestr, fractional, tzname, tzhour, tzmin = m.groups()
    #print "datetimeutils:196", datestr, '*', tzname, '*', tzhour, '*', tzmin

    # Create tzinfo object representing the timezone expressed in the input
    # string.  The names we give for the timezones are lame: they are just the
    # offset from UTC (as it appeared in the input string).  Handle UTC
    # specially since it is a very common case and we know its name.
    if tzname is None:
        tz = None
    else:
        tzhour, tzmin = int(tzhour), int(tzmin)
        if tzhour == tzmin == 0:
            tzname = 'UTC'
        tz = FixedOffset(timedelta(hours=tzhour,
                                   minutes=tzmin), tzname)

    # Convert the date/time field into a python datetime object.
    try:
        x = datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        x = datetime.strptime(datestr, "%Y-%m-%d")
    #print "datetimeutils:214", x

    # Convert the fractional second portion into a count of microseconds.
    if fractional is None:
        fractional = '0'
    fracpower = 6 - len(fractional)
    fractional = float(fractional) * (10 ** fracpower)

    # Return updated datetime object with microseconds and timezone information
    y = x.replace(microsecond=int(fractional), tzinfo=tz)
    #print "datetimeutils:224", y
    return y
