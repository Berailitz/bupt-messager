import functools
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from .config import SQLALCHEMY_DATABASE_URI
from .models import Attachment, Base, Chat, Notification

def use_session():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            with args[0].sql_manager.create_session() as my_session:
                return func(my_session, *args[1:], **kw)
        return wrapper
    return decorator

class SQLManager(object):
    def __init__(self):
        Notification.attachments = relationship("Attachment", order_by=Attachment.id, back_populates="notice")
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        Base.metadata.create_all(engine)
        session_factory = sessionmaker(bind=engine)
        self.session_maker = scoped_session(session_factory)

    @contextmanager
    def create_session(self):
        """Create session to talk to database."""
        session = self.session_maker
        try:
            yield session
            # session.commit()
        except Exception as identifier:
            logging.exception(identifier)
            session.rollback()
            raise identifier
        finally:
            session.close()
            self.session_maker.remove()

class SQLHandle(object):
    def __init__(self, sql_manager=None):
        self.sql_manager = sql_manager

    def init_sql_manager(self, sql_manager=None):
        if sql_manager:
            self.sql_manager = sql_manager
        else:
            logging.warning('SQLHandle: No `sql_manager` specified, another `scoped_session` will be opened.')
            self.sql_manager = SQLManager()

    @use_session()
    def is_new_notice(my_session, notice_id):
        return not my_session.query(Notification).filter(Notification.id==notice_id).all()

    @use_session()
    def insert_notice(my_session, notice_dict):
        attachment_list = [Attachment(**attachment_dict) for attachment_dict in notice_dict.pop('attachments')]
        new_notice = Notification(**notice_dict)
        new_notice.attachments = attachment_list
        logging.info(f'SQLHandle: Adding notice `{new_notice.title}` with {len(attachment_list)} attachments.')
        my_session.add(new_notice)
        my_session.commit()
        return new_notice

    @use_session()
    def get_latest_notices(my_session, length, start=0):
        return my_session.query(Notification).order_by(Notification.date).all()[start:length]

    @use_session()
    def get_chat_ids(my_session):
        return [chat.id for chat in my_session.query(Chat).all()]

    @use_session()
    def insert_chat(my_session, new_id):
        if not my_session.query(Chat).filter(Chat.id==new_id).all():
            new_chat = Chat(id=new_id)
            my_session.add(new_chat)
            my_session.commit()
            return new_chat
        return None
