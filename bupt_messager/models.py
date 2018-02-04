from sqlalchemy import Column, Date, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

"""
CREATE TABLE `notification` (
  `id` varchar(36) NOT NULL,
  `text` text NOT NULL,
  `title` varchar(80) NOT NULL,
  `url` text NOT NULL,
  `summary` text NOT NULL,
  `date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""
class Notification(Base):
    __tablename__ = 'notification'
    id = Column(String(36), primary_key=True)
    text = Column(Text)
    title = Column(String(80))
    url = Column(Text)
    summary = Column(Text)
    date = Column(Date)

    def __repr__(self):
        return f"<Notification(id='{self.id}', title='{self.title}')>"

"""
CREATE TABLE `attachment` (
  `id` int(11) NOT NULL,
  `notice_id` varchar(36) NOT NULL,
  `name` varchar(50) NOT NULL,
  `url` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""
class Attachment(Base):
    __tablename__ = 'attachment'
    id = Column(Integer, primary_key=True)
    notice_id = Column(String(36), ForeignKey('notification.id'))
    name = Column(String(50))
    url = Column(Text)

    notice = relationship("Notification", back_populates="attachments")

    def __repr__(self):
        return f"<Attachment(name='{self.name}')>"

"""
CREATE TABLE `chat` (
  `id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""
class Chat(Base):
    __tablename__ = 'chat'
    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f"<Chat(id='{self.id}')>"
