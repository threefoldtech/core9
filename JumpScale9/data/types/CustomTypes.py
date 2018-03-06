# from js9 import j
from JumpScale9 import j
'''Definition of several custom types (paths, ipaddress, guid,...)'''

import re

from .PrimitiveTypes import String, Integer

class Guid(String):
    '''Generic GUID type'''

    NAME = 'guid'

    def __init__(self):
        String.__init__(self)
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

    NAME = 'email'

    def __init__(self):
        String.__init__(self)
        
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
    NAME = 'path'

    def __init__(self):
        String.__init__(self)        
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
    NAME = 'tel'

    def __init__(self):
        String.__init__(self)
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
    NAME = 'iprange'

    def __init__(self):
        String.__init__(self)
        self._RE = re.compile(
            '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}')

    def get_default(self):
        return "192.168.1.1/24"


class IPAddress(String):
    """
    """
    NAME = 'ipaddress'

    def __init__(self):
        String.__init__(self)        
        self._RE = re.compile('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')

    def get_default(self):
        return "192.168.1.1"


class IPPort(Integer):
    '''Generic IP port type'''
    NAME = 'ipport'

    def __init__(self):
        Integer.__init__(self)        
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
    NAME = 'numeric'

    def __init__(self):
        String.__init__(self)
    
    def get_default(self):
        return "0 USD"


class Date(String):
    '''
    Date in year/month/day format
    '''
    NAME = 'date'

    def __init__(self):
        String.__init__(self)        
        self._RE = re.compile('[0-9]{4}/[0-9]{2}/[0-9]{2}')

    def get_default(self):
        return "-1"

    def check(self, value):
        '''
        Check whether provided value is a valid tel nr
        '''
        if not j.data.types.string.check(value):
            return False
        value = self.clean(value)
        return self._RE.fullmatch(value) is not None

    def fromString(self, txt):
        try:
            epoch = int(txt)
            if epoch == 0:
                return ""
            txt = j.data.time.epoch2HRDate(epoch)
        except Exception as  e:
            raise  e        
        if self.check(txt) == False:
            raise RuntimeError("is not date:%s"%txt)
        return txt

    def clean(self, v):
        if j.data.types.string.check(v):
            return v
        elif not j.data.types.string.check(v):
            raise ValueError("Input needs to be string:%s" % v)
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
    NAME = 'duration'
    
    def __init__(self):
        String.__init__(self)
        
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

