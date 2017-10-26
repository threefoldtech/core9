from protobuf3.message import Message
from protobuf3.fields import StringField, MessageField, EnumField, UInt32Field
from service import ServicePointer
from domain import DomainPointer
from enum import Enum


class JobRequest(Message):
    pass


class Job(Message):

    class Status(Enum):
        INIT = 0
        RUNNING = 1
        OK = 2
        ERROR = 3


class JobRecurring(Message):

    class Status(Enum):
        INIT = 0
        OK = 1
        ERROR = 2
        SCHEDULED = 3

JobRequest.add_field('guid', StringField(field_number=1, optional=True))
JobRequest.add_field('service', MessageField(field_number=2, optional=True, message_cls=ServicePointer))
JobRequest.add_field('action', StringField(field_number=3, optional=True))
JobRequest.add_field('domain', MessageField(field_number=4, optional=True, message_cls=DomainPointer))
JobRequest.add_field('args', StringField(field_number=5, optional=True))
JobRequest.add_field('state_start', UInt32Field(field_number=6, optional=True))
JobRequest.add_field('deadline', UInt32Field(field_number=7, optional=True))
JobRequest.add_field('maxretry', UInt32Field(field_number=8, optional=True))
JobRequest.add_field('recurring_period', UInt32Field(field_number=9, optional=True))
Job.add_field('guid', StringField(field_number=1, optional=True))
Job.add_field('jobrequest_guid', StringField(field_number=2, optional=True))
Job.add_field('service', MessageField(field_number=3, optional=True, message_cls=ServicePointer))
Job.add_field('action', StringField(field_number=4, optional=True))
Job.add_field('domain', MessageField(field_number=5, optional=True, message_cls=DomainPointer))
Job.add_field('status', EnumField(field_number=6, optional=True, enum_cls=Job.Status))
Job.add_field('args', StringField(field_number=7, optional=True))
Job.add_field('time_start', UInt32Field(field_number=8, optional=True))
Job.add_field('time_stop', UInt32Field(field_number=9, optional=True))
JobRecurring.add_field('guid', StringField(field_number=1, optional=True))
JobRecurring.add_field('service', MessageField(field_number=2, optional=True, message_cls=ServicePointer))
JobRecurring.add_field('action', StringField(field_number=3, optional=True))
JobRecurring.add_field('domain', MessageField(field_number=4, optional=True, message_cls=DomainPointer))
JobRecurring.add_field('status', EnumField(field_number=5, optional=True, enum_cls=JobRecurring.Status))
JobRecurring.add_field('args', StringField(field_number=6, optional=True))
JobRecurring.add_field('startdate', UInt32Field(field_number=7, optional=True))
JobRecurring.add_field('deadline', UInt32Field(field_number=8, optional=True))
JobRecurring.add_field('maxretry', UInt32Field(field_number=9, optional=True))
