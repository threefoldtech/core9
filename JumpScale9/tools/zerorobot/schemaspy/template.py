from protobuf3.message import Message
from protobuf3.fields import EnumField, Int32Field, MessageField, BoolField, StringField
from enum import Enum
from domain import Domain, DomainPointer


class Template(Message):

    class TemplateStatus(Enum):
        NEW = 0
        OK = 1
        ERROR = 2
        DISABLED = 3


class TemplatePointer(Message):
    pass


class TemplateConsumption(Message):
    pass


class TemplateParent(Message):
    pass


class TemplateActionConsumption(Message):
    pass


class TemplateAction(Message):
    pass

Template.add_field('guid', StringField(field_number=1, optional=True))
Template.add_field('previous', StringField(field_number=2, optional=True))
Template.add_field('name', StringField(field_number=3, optional=True))
Template.add_field('version', Int32Field(field_number=4, optional=True))
Template.add_field('domain', MessageField(field_number=5, optional=True, message_cls=DomainPointer))
Template.add_field('status', EnumField(field_number=6, optional=True, enum_cls=Template.TemplateStatus))
Template.add_field('consumptions', MessageField(field_number=7, repeated=True, message_cls=TemplateConsumption))
Template.add_field('parent', MessageField(field_number=8, optional=True, message_cls=TemplateParent))
Template.add_field('actions', MessageField(field_number=9, repeated=True, message_cls=TemplateAction))
Template.add_field('dataschema', StringField(field_number=10, optional=True))
TemplatePointer.add_field('guid', StringField(field_number=1, optional=True))
TemplatePointer.add_field('name', StringField(field_number=2, optional=True))
TemplatePointer.add_field('domain', MessageField(field_number=3, optional=True, message_cls=DomainPointer))
TemplateConsumption.add_field('template_name', StringField(field_number=1, optional=True))
TemplateConsumption.add_field('template_minversion', Int32Field(field_number=2, optional=True))
TemplateConsumption.add_field('template_domain', MessageField(field_number=3, optional=True, message_cls=Domain))
TemplateConsumption.add_field('min_nr', Int32Field(field_number=4, optional=True))
TemplateConsumption.add_field('max_nr', Int32Field(field_number=5, optional=True))
TemplateConsumption.add_field('auto', BoolField(field_number=6, optional=True))
TemplateConsumption.add_field('argname', StringField(field_number=7, optional=True))
TemplateParent.add_field('template_name', StringField(field_number=1, optional=True))
TemplateParent.add_field('template_domain', MessageField(field_number=2, optional=True, message_cls=Domain))
TemplateParent.add_field('template_minversion', Int32Field(field_number=3, optional=True))
TemplateParent.add_field('argname', StringField(field_number=4, optional=True))
TemplateActionConsumption.add_field('template_name', StringField(field_number=1, optional=True))
TemplateActionConsumption.add_field('action_name', StringField(field_number=2, optional=True))
TemplateAction.add_field('name', StringField(field_number=1, optional=True))
TemplateAction.add_field('code', StringField(field_number=2, optional=True))
TemplateAction.add_field('consumptions', MessageField(field_number=3, repeated=True, message_cls=TemplateActionConsumption))
