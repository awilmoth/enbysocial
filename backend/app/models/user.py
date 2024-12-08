from datetime import datetime
from peewee import *
from app.database import BaseModel

class User(BaseModel):
    id = AutoField()
    username = CharField(unique=True, null=False)
    email = CharField(unique=True, null=False)
    password_hash = CharField(null=False)
    profile_picture = CharField(null=True)
    created_at = TimestampField(null=False, default=datetime.now)
    last_login = TimestampField(null=True)
    latitude = DoubleField(null=True)
    longitude = DoubleField(null=True)
    last_location_update = TimestampField(null=True)

    class Meta:
        table_name = "user"

class PersonalAd(BaseModel):
    id = AutoField()
    user = ForeignKeyField(model=User, backref='personal_ads', on_delete='CASCADE')
    content = TextField(null=False)
    created_at = TimestampField(null=False, default=datetime.now)
    updated_at = TimestampField(null=False, default=datetime.now)
    latitude = DoubleField(null=False)
    longitude = DoubleField(null=False)
    is_active = BooleanField(null=False, default=True)

    class Meta:
        table_name = "personalad"
        indexes = (
            (('user_id',), False),
            (('is_active',), False),
        )

class Message(BaseModel):
    id = AutoField()
    sender = ForeignKeyField(model=User, backref='sent_messages', on_delete='CASCADE')
    receiver = ForeignKeyField(model=User, backref='received_messages', on_delete='CASCADE')
    content = TextField(null=False)
    created_at = TimestampField(null=False, default=datetime.now)
    is_read = BooleanField(null=False, default=False)
    read_at = TimestampField(null=True)

    class Meta:
        table_name = "message"
        indexes = (
            (('sender_id',), False),
            (('receiver_id',), False),
            (('is_read',), False),
        )
