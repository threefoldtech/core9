from protobuf3.message import Message
from protobuf3.fields import StringField


class Domain(Message):
    pass


class DomainPointer(Message):
    pass

Domain.add_field('guid', StringField(field_number=1, optional=True))
Domain.add_field('name', StringField(field_number=2, optional=True))
Domain.add_field('pubkey', StringField(field_number=3, optional=True))
DomainPointer.add_field('guid', StringField(field_number=1, optional=True))
DomainPointer.add_field('name', StringField(field_number=2, optional=True))
