# from js9 import j
from JumpScale9 import j
'''Definition of several custom types (paths, ipaddress, guid,...)'''

import re

from .PrimitiveTypes import String, Integer

class Guid(String):
    '''Generic GUID type'''

    def __init__(self):
        String.__init__(self)
        self.NAME = 'guid'
        self._RE = re.compile(
            '^[0-9a-fA-F]{8}[-:][0-9a-fA-F]{4}[-:][0-9a-fA-F]{4}[-:][0-9a-fA-F]{4}[-:][0-9a-fA-F]{12}$')

    def check(self, value):
        '''Check whether provided value is a valid GUID string'''
        if not j.data.types.string.check(value):
            return False
        return self._RE.match(value) is not None

    def get_default(self):
        return j.data.idgenerator.generateGUID()

    def fromString(self, v):
        if not j.data.types.string.check(v):
            raise ValueError("Input needs to be string:%s" % v)
        if self.check(s):
            return s
        else:
            raise ValueError("%s not properly formatted: '%s'" %
                             (Guid.NAME, v))

    toString = fromString


class Email(String):
    """
    """

    def __init__(self):
        String.__init__(self)
        self.NAME = 'email'
        self._RE = re.compile(
            '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    def check(self, value):
        '''
        Check whether provided value is a valid tel nr
        '''
        if not j.data.types.string.check(value):
            return False
        value = self.clean(value)
        return self._RE.fullmatch(value) is not None

    def clean(self, v):
        if not j.data.types.string.check(v):
            raise ValueError("Input needs to be string:%s" % v)
        v = v.lower()
        v.strip()
        return v

    def fromString(self, v):
        v = self.clean(v)
        if self.check(v):
            return v
        else:
            raise ValueError("%s not properly formatted: '%s'" %
                             (self.NAME, v))

    toString = fromString

    def get_default(self):
        return "changeme@example.com"


class Path(String):
    '''Generic path type'''

    def __init__(self):
        String.__init__(self)
        self.NAME = 'path'
        self._RE = re.compile('.*')

    def get_default():
        return ""


class Tel(String):
    """
    format is e.g. +32 475.99.99.99x123
    only requirement is it needs to start with +
    the. & , and spaces will not be remembered
    and x stands for phone number extension
    """

    def __init__(self):
        String.__init__(self)
        self.NAME = 'tel'
        self._RE = re.compile('^\+?[0-9]{6,15}(?:x[0-9]+)?$')

    def clean(self, v):
        if not j.data.types.string.check(v):
            raise ValueError("Input needs to be string:%s" % v)
        v = v.replace(".", "")
        v = v.replace(",", "")
        v = v.replace("-", "")
        v = v.replace("(", "")
        v = v.replace(")", "")
        v = v.replace(" ", "")
        v.strip()
        return v

    def get_default(self):
        return "+32 475.99.99.99"


class IPRange(String):
    """
    """

    def __init__(self):
        String.__init__(self)
        self.NAME = 'iprange'
        self._RE = re.compile(
            '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}')

    def get_default(self):
        return "192.168.1.1/24"


class IPAddress(String):
    """
    """

    def __init__(self):
        String.__init__(self)
        self.NAME = 'ipaddress'
        self._RE = re.compile('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')

    def get_default(self):
        return "192.168.1.1"


class IPPort(Integer):
    '''Generic IP port type'''

    def __init__(self):
        Integer.__init__(self)
        self.NAME = 'ipport'
        self.BASETYPE = 'string'

    def check(self, value):
        '''
        Check if the value is a valid port
        We just check if the value a single port or a range
        Values must be between 0 and 65535
        '''
        if not Integer.check(self, value):
            return False
        if 0 < value <= 65535:
            return True
        return False


class Numeric(String):
    """
    has support for currencies
    """

    def __init__(self):
        String.__init__(self)
        self.NAME = 'numeric'
        

    def get_default(self):
        return "0 USD"


class Date(String):
    '''
    Date
    -1 is indefinite in past
    0 is now
    +1 is indefinite in future
    +1d will be converted to 1 day from now, 1 can be any int
    +1w will be converted to 1 week from now, 1 can be any int
    +1w_end will be converted to 1 week from now at end of week (Saturday), 1 can be any int
    +1m_end will be converted to 1 week from now at end of month (last day of month), 1 can be any int
    '''

    def __init__(self):
        String.__init__(self)
        self.NAME = 'date'
        self._RE = re.compile('[0-9]{2}/[0-9]{2}/[0-9]{4}')
        self._RE_days = re.compile('^\+\dd')
        self._RE_weeks = re.compile('^\+\dw')

    def get_default(self):
        return "-1"

    def check(self, value):
        '''
        Check whether provided value is a valid tel nr
        '''
        if not j.data.types.string.check(value):
            return False
        value = self.clean(value)
        if value in ["-1", "+1", "0", ""]:
            return True
        return self._RE.fullmatch(value) is not None

    def clean(self, v):
        if j.data.types.string.check(v):
            if v.count("-") > 1:
                v = v.replace("-", ":")

        if v == -1:
            v = "-1"
        elif v == 1:
            v = "+1"
        elif v == 0:
            v == "0"
        elif not j.data.types.string.check(v):
            raise ValueError("Input needs to be string:%s" % v)
        elif self._RE_days.fullmatch(value) is not None:
            j.application.break_into_jshell("DEBUG NOW day extra")
        elif self._RE_weeks.fullmatch(value) is not None:
            j.application.break_into_jshell("DEBUG NOW week extra")
        return v


class Duration(String):
    '''
    Duration type

    Understood formats:
    - #w week
    - #d days
    - #h hours
    - #m minutes
    - #s seconds

    e.g. 10d is 10 days
    if int then in seconds

    -1 is infinite

    '''

    def __init__(self):
        String.__init__(self)
        self.NAME = 'duration'
        self._RE = re.compile('^(\d+)([wdhms]?)$')

    def check(self, value):
        if isinstance(value, int):
            if value == -1:
                return True
            elif value >= 0:
                return True
        elif isinstance(value, str):
            if self.fullmatch(value):
                return True
        return False

    def convertToSeconds(self, value):
        """Translate a string representation of a duration to an int
        representing the amount of seconds.

        Understood formats:
        - #w week
        - #d days
        - #h hours
        - #m minutes
        - #s seconds

        @param value: number or string representation of a duration in the above format
        @type value: string or int
        @return: amount of seconds
        @rtype: int
        """
        if not isinstance(value, str):
            return value
        m = self._RE.match(value)
        if m:
            # Ok, valid format
            amount, granularity = m.groups()
            amount = int(amount)
            if granularity == 'w':
                multiplier = 60 * 60 * 24 * 7
            elif granularity == 'd':
                multiplier = 60 * 60 * 24
            elif granularity == 'h':
                multiplier = 60 * 60
            elif granularity == 'm':
                multiplier = 60
            elif granularity == 's':
                multiplier = 1
            else:
                # Default to seconds
                multiplier = 1
            return amount * multiplier
        return value

