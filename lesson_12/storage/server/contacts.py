from peewee import AutoField, ForeignKeyField

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
    def delete_by_client(cls, *args, **kwargs):
        client = Client.get(*args, **kwargs)
        contact = cls.get(cls.client_id == client.id)
        if contact is not None:
            contact.delete_instance()
            contact.save()

    @classmethod
    def list(cls, *args, **kwargs):
        result = []
        for user in Client.select(Client.name).join(cls):
            result.append(user.name)
        return result