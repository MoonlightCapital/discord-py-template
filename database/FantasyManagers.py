from umongo import Document
from umongo.fields import *

from internal.database_init import instance

@instance.register
class FantasyManagers(Document):
    """
    This document stores information about how many times all particular users have been reprimanded
    """

    user = StringField(attribute='_id', required=True)
    team = IntegerField(required=True)
    league = StringField(required=True)

    class Meta:
        collection_name = "manager"
