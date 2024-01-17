from ..session import with_session
from typing import Dict, List
import uuid 
from ..models.message_model import MessageModel

@with_session
def add_message_to_db(session, converation_id:str, chat_type, query, response='', message_id=None, meta_data:dict={}):
    '''
    add message to message table 
    '''

    if not message_id:
        message_id = uuid.uuid4().hex
    if not converation_id: 
        converation_id = uuid.uuid4().hex
    m = MessageModel(id=message_id, chat_type=chat_type, converation_id=converation_id, query=query, response=response, meta_data=meta_data)
    session.add(m)
    session.commit()

    return m.id
