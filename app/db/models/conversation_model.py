from sqlalchemy import Column, String, DateTime, func
from ..base import Base


class ConversationModel(Base):
    """
    conversation table
    """

    __tablename__ = "conversation"
    id = Column(String(32), primary_key=True, comment="ID")
    name = Column(String(50), comment="Dialog Name")
    chat_type = Column(String(50), comment="Chat Type")
    create_time = Column(DateTime, default=func.now(), comment="Creation Time")

    def __repr__(self):
        return f"<converation(id={self.id}), name={self.name}, chat_type={self.chat_type}, create_time={self.create_time}"
