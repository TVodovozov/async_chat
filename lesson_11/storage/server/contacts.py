from peewee import AutoField, ForeignKeyField, Model, DoesNotExist

from storage import BaseModel
from storage.server.client import Client
from storage.server.history import History


class Contacts(BaseModel):
    id = AutoField(primary_key=True)
    client_id = ForeignKeyField(Client, unique=True)
    history_id = ForeignKeyField(History)

    class Meta:
        table_name = "Contacts"

    @classmethod
    def delete_by_client(cls, client: Client, **kwargs):
        _id = client.get(**kwargs)
        contact = cls.get(client_id=_id)
        contact.delete_instance()