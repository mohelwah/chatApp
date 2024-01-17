from sqlalchemy import Column, Integer, String, DateTime, JSON, func

from ..base import Base


class MessageModel(Base):
    """
    Message table
    """

    __tablename__ = "message"
    id = Column(String(32), primary_key=True, comment="ID")
    converation_id = Column(
        String(32), default=None, index=True, comment="Conceration ID"
    )
    chat_type = Column(String(50), comment="Chat Type")
    query = Column(String(4096), comment="Query")
    response = Column(String(4096), comment="Response")
    meta_data = Column(JSON, default={})
    feedback_score = Column(Integer, default=-1, comment="Feedback score")
    feedback_reason = Column(String(255), default="", comment="Feedback Reason")
    create_time = Column(DateTime, default=func.now(), comment="Creation Time")

    def __repr__(self):
        return f"<message(id='{self.id}', conversation_id='{self.conversation_id}', chat_type='{self.chat_type}', query='{self.query}', response='{self.response}',meta_data='{self.meta_data}',feedback_score='{self.feedback_score}',feedback_reason='{self.feedback_reason}', create_time='{self.create_time}')>"
