from datetime import datetime

from peewee import AutoField, DateField, CharField, TextField, BooleanField, IntegerField

from storage import BaseModel


class Messages(BaseModel):
    id = AutoField(primary_key=True)
    session = IntegerField(null=False)
    sender = CharField(null=False, unique=True)
    recipient = CharField(null=False, unique=True)
    message = TextField(null=False, unique=False)
    created = DateField(null=False, default=datetime.utcnow())
    is_private = BooleanField(default=False)

    class Meta:
        table_name = "Messages"