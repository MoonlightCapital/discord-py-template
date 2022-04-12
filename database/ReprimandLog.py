from umongo import Document, validate
from umongo.fields import *

from internal.database_init import instance

@instance.register
class ReprimandLog(Document):
    """
    This document stores information about how many times all particular users have been reprimanded
    """

    user = StringField(attribute='_id', required=True)
    count = IntegerField(default=1)

    class Meta:
        collection_name = "record"
