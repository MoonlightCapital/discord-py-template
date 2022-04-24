from umongo import Document
from umongo.fields import *

from internal.database_init import instance

@instance.register
class AutoReply(Document):
    """
    This document stores information about users who have set up an auto reply message for when they are tagged.
    """

    user = StringField(attribute='_id', required=True)
    message = StringField(default='')

    class Meta:
        collection_name = "autoreply"
