"""Models representing SQL tables."""
from sqlalchemy import Column, Date, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func as sql_func
from .config import STATUS_TEXT_DICT

Base = declarative_base()


class Notification(Base):
    """Table notification.

        :member id: Notice id.
        :type id: int.
        :member text: Text of the notice.
        :type text: str.
        :member title: Title of the notice.
        :type title: str.
        :member url: URL to the notice.
        :type url: str.
        :member summary: summary of the notice.
        :type summary: str.
        :member date: Date of the notice.
        :type date: str.
    """
    __tablename__ = 'notification'
    id = Column(String(36), primary_key=True)
    text = Column(Text)
    title = Column(String(80))
    url = Column(Text)
    summary = Column(Text)
    date = Column(Date)

    def __repr__(self):
        return f"<Notification(id='{self.id}', title='{self.title}')>"


class Attachment(Base):
    """Table attachment.

        :member id: Attachment id.
        :type id: int.
        :member notice_id: Id of attached notice.
        :type notice_id: str.
        :member name: Name of the attachment.
        :type name: str.
        :member url: URL to the attachment.
        :type url: str.
    """
    __tablename__ = 'attachment'
    id = Column(Integer, primary_key=True)
    notice_id = Column(String(36), ForeignKey('notification.id'))
    name = Column(String(50))
    url = Column(Text)

    notice = relationship("Notification", back_populates="attachments")

    def __repr__(self):
        return f"<Attachment(name='{self.name}')>"


class Chat(Base):
    """Table chat.

    Attributes:
        :member id: Chat id.
        :type id: int.
    """
    __tablename__ = 'chat'
    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f"<Chat(id='{self.id}')>"


class Status(Base):
    """Table status.

    Attributes:
        :member status: Status code.
        :type status: int.
        :member time: Timestamp.
        :type time: datetime.datetime.
    """
    __tablename__ = 'status'
    status = Column(Integer)
    time = Column(DateTime, primary_key=True, default=sql_func.now(), onupdate=sql_func.now())

    def __repr__(self):
        return f"<Status(status={self.status_text}, time='{self.time}')>"

    @property
    def status_text(self) -> str:
        """Property, status in text.
        """
        return STATUS_TEXT_DICT[self.status]
