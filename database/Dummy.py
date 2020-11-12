from umongo import Document, validate
from umongo.fields import *

from internal.database_init import instance

@instance.register
class Dummy(Document):
    """A dummy document type, to show how to operate with the database"""

    title = StringField(required=True, max_length=200)
    content = StringField(required=True)
    author = StringField(required=True, max_length=50)
