from protobuf3.message import Message
from protobuf3.fields import StringField, MessageField, Int32Field, EnumField
from enum import Enum
from domain import DomainPointer
from template import TemplatePointer


class Service(Message):

    class ServiceStatus(Enum):
        NEW = 0
        OK = 1
        ERROR = 2
        DISABLED = 3


class ServicePointer(Message):
    pass


class ServiceConsumption(Message):

    class ServiceConsumptionStatus(Enum):
        NEW = 0
        OK = 1
        ERROR = 2
        DISABLED = 3


class ActionConsumption(Message):

    class ActionConsumptionStatus(Enum):
        NEW = 0
        OK = 1
        ERROR = 2
        DISABLED = 3


class ServiceAction(Message):
    pass

Service.add_field('guid', StringField(field_number=1, optional=True))
Service.add_field('previous', StringField(field_number=2, optional=True))
Service.add_field('version', Int32Field(field_number=3, optional=True))
Service.add_field('instance', StringField(field_number=4, optional=True))
Service.add_field('domain', MessageField(field_number=5, optional=True, message_cls=DomainPointer))
Service.add_field('template', MessageField(field_number=6, optional=True, message_cls=TemplatePointer))
Service.add_field('status', EnumField(field_number=7, optional=True, enum_cls=Service.ServiceStatus))
Service.add_field('consumptions', MessageField(field_number=8, repeated=True, message_cls=ServiceConsumption))
Service.add_field('parent', MessageField(field_number=9, optional=True, message_cls=ServicePointer))
Service.add_field('actions', MessageField(field_number=10, repeated=True, message_cls=ServiceAction))
ServicePointer.add_field('guid', StringField(field_number=1, optional=True))
ServicePointer.add_field('instance', StringField(field_number=2, optional=True))
ServicePointer.add_field('name', StringField(field_number=3, optional=True))
ServicePointer.add_field('domain', MessageField(field_number=4, optional=True, message_cls=DomainPointer))
ServiceConsumption.add_field('service', MessageField(field_number=1, optional=True, message_cls=ServicePointer))
ServiceConsumption.add_field('status', EnumField(field_number=2, optional=True, enum_cls=ServiceConsumption.ServiceConsumptionStatus))
ActionConsumption.add_field('service', MessageField(field_number=1, optional=True, message_cls=ServicePointer))
ActionConsumption.add_field('action_name', StringField(field_number=2, optional=True))
ActionConsumption.add_field('status', EnumField(field_number=3, optional=True, enum_cls=ActionConsumption.ActionConsumptionStatus))
ServiceAction.add_field('name', StringField(field_number=1, optional=True))
ServiceAction.add_field('consumption', MessageField(field_number=2, repeated=True, message_cls=ActionConsumption))
