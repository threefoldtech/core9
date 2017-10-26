from protobuf3.message import Message
from protobuf3.fields import StringField, MessageField, EnumField
from enum import Enum
from domain import DomainPointer


class ZeroRobot(Message):

    class Status(Enum):
        INIT = 0
        OK = 1
        ERROR = 2
        SCHEDULED = 3


class ZerorobotPointer(Message):
    pass


class Location(Message):

    class Status(Enum):
        INIT = 0
        OK = 1
        ERROR = 2
        SCHEDULED = 3


class LocationPointer(Message):
    pass

ZeroRobot.add_field('guid', StringField(field_number=1, optional=True))
ZeroRobot.add_field('domain', MessageField(field_number=2, optional=True, message_cls=DomainPointer))
ZeroRobot.add_field('description', StringField(field_number=3, optional=True))
ZeroRobot.add_field('location', MessageField(field_number=4, optional=True, message_cls=LocationPointer))
ZeroRobot.add_field('status', EnumField(field_number=5, optional=True, enum_cls=ZeroRobot.Status))
ZeroRobot.add_field('ipaddr', StringField(field_number=6, optional=True))
ZerorobotPointer.add_field('guid', StringField(field_number=1, optional=True))
ZerorobotPointer.add_field('domain', MessageField(field_number=2, optional=True, message_cls=DomainPointer))
Location.add_field('guid', StringField(field_number=1, optional=True))
Location.add_field('domain', MessageField(field_number=2, optional=True, message_cls=DomainPointer))
Location.add_field('description', StringField(field_number=3, optional=True))
Location.add_field('status', EnumField(field_number=4, optional=True, enum_cls=Location.Status))
LocationPointer.add_field('guid', StringField(field_number=1, optional=True))
LocationPointer.add_field('name', StringField(field_number=2, optional=True))
LocationPointer.add_field('domain', MessageField(field_number=3, optional=True, message_cls=DomainPointer))
