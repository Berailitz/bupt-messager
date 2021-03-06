"""Handle SQL-related requests."""
import functools
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Callable, List, Union
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import joinedload, relationship, scoped_session, sessionmaker
from sqlalchemy.orm.session import Session
from .config import SQLALCHEMY_DATABASE_URI
from .mess import fun_logger
from .models import Attachment, Base, Chat, Notification, Status, SubscriberChannel


class SQLManager(object):
    """Manager sessions.

    :member session_maker: Attached :obj: sessionmaker.
    :type session_maker: :obj:sessionmaker.
    """
    def __init__(self):
        Notification.attachments = relationship("Attachment", order_by=Attachment.id, back_populates="notice")
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        Base.metadata.create_all(engine)
        session_factory = sessionmaker(bind=engine)
        self.session_maker = scoped_session(session_factory)

    @contextmanager
    def create_session(self):
        """Create session to talk to database, rollback and raise error if failed.
        """
        session = self.session_maker
        try:
            yield session
        except Exception as identifier:
            logging.exception(identifier)
            session.rollback()
            raise identifier
        finally:
            session.close()
            self.session_maker.remove()


def load_session(func: Callable):
    """Load new session and add session as the first argument of `func`.

    :param func: Target function.
    :type func: function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kw):
        """See `load_session`
        """
        with args[0].sql_manager.create_session() as my_session:
            return func(my_session, *args[1:], **kw)
    return wrapper


class SQLHandler(object):
    """Handler for SQL requests.
    """
    def __init__(self, sql_manager=None):
        self.sql_manager = sql_manager

    def init_sql_manager(self, sql_manager=None):
        """Initialize SQLHandler with `sql_manager`.

        :param sql_manager: Manage sessions, defaults to `None`.
        :type sql_manager: SQLManager, optional.
        """
        if sql_manager:
            self.sql_manager = sql_manager
        else:
            logging.warning('SQLHandler: No `sql_manager` specified, another `scoped_session` will be opened.')
            self.sql_manager = SQLManager()

    @load_session
    def is_new_notice(my_session: Session, notice_id: int):
        """Check whether `notice_id` exists.

        :param my_session: Current session.
        :type my_session: Session.
        :param notice_id: New notice id.
        :type notice_id: int.
        """
        return not my_session.query(exists().where(Notification.id==notice_id)).scalar()

    @load_session
    @fun_logger(log_fun=logging.debug)
    def insert_notice(my_session: Session, notice_dict: dict):
        """Insert new notice to SQL.

        :param my_session: Cureent session.
        :type my_session: Session.
        :param notice_dict: Dict representing new notice.
        :type notice_dict: dict.
        """
        attachment_list = [Attachment(**attachment_dict) for attachment_dict in notice_dict.pop('attachments')]
        new_notice = Notification(**notice_dict)
        new_notice.attachments = attachment_list
        logging.info(f'SQLHandler: Adding notice `{new_notice.title}` with {len(attachment_list)} attachments.')
        my_session.add(new_notice)
        my_session.commit()
        return my_session.query(Notification).options(joinedload('attachments')).filter(Notification.id == notice_dict['id']).one_or_none()

    @load_session
    @fun_logger(log_fun=logging.debug)
    def get_notice(my_session: Session, notice_id: str) -> Union[Notification, None]:
        """Retrive one notice.

        :param my_session: Cureent session.
        :type my_session: Session.
        :param notice_id: ID of the notice_id.
        :type notice_id: str.
        :return: The notice.
        :rtype: Notification or None.
        """
        return my_session.query(Notification).options(joinedload('attachments')).filter(Notification.id == notice_id).one_or_none()

    @load_session
    @fun_logger(log_fun=logging.debug)
    def get_latest_notices(my_session: Session, length: int, start: int = 0) -> List:
        """Retrive noticess with most recent `date`s.

        :param my_session: Cureent session.
        :type my_session: Session.
        :param length: Amont of the notices retrived.
        :type length: int.
        :param start: Count from the notice at index `start`, defaults to `0`
        :type start: int.
        :return: List of :obj:`Notice`s.
        :rtype: list.
        """
        return my_session.query(Notification).options(joinedload('attachments')).order_by(Notification.time.desc()).all()[start:][:length]

    @load_session
    def get_chat_ids(my_session: Session, channel: SubscriberChannel = SubscriberChannel.AllChannel) -> List[int]:
        """Retrive all chat ids.

        :param my_session: Current session.
        :type my_session: Session.
        :param channel: User channel.
        :type channel: SubscriberChannel, `all`(default), `normal`, `insider`.
        :return: List of `id`s.
        :rtype: List[int].
        """
        if channel == SubscriberChannel.NormalChannel:
            return [chat.id for chat in my_session.query(Chat).filter(Chat.is_insider==False).all()]
        elif channel == SubscriberChannel.InsiderChannel:
            return [chat.id for chat in my_session.query(Chat).filter(Chat.is_insider==True).all()]
        else:
            return [chat.id for chat in my_session.query(Chat).all()]

    @load_session
    def insert_chat(my_session: Session, new_id: int) -> int:
        """Insert chat id.

        :param my_session: Current session.
        :type my_session: Session.
        :param new_id: Chat id.
        :type new_id: int.
        """
        if not my_session.query(exists().where(Chat.id==new_id)).scalar():
            new_chat = Chat(id=new_id)
            my_session.add(new_chat)
            my_session.commit()
            return new_id
        return None

    @load_session
    def remove_chat(my_session: Session, old_id: int):
        """Remove chat id.

        :param my_session: Current session.
        :type my_session: Session.
        :param old_id: Chat id.
        :type old_id: int.
        """
        old_chat = my_session.query(Chat).filter(Chat.id == old_id).one_or_none()
        if old_chat is None:
            logging.warning(f"SQLHandler: Duplicate remove of chat `{old_id}`.")
        else:
            my_session.delete(old_chat)
            my_session.commit()

    @load_session
    @fun_logger(log_fun=logging.debug)
    def get_latest_status(my_session: Session, start: datetime, end: datetime = None) -> List[Status]:
        """Retrive :obj:`Status` by time.

        :param my_session: Current session.
        :type my_session: Session.
        :param start: Start time of the list of :obj:`Status`s.
        :type start: datetime.
        :param end: Defaults to None. Start time of the list of :obj:`Status`s.
        :type end: datetime.
        :rtype: List[Status].
        """
        if end is None:
            end = datetime.now()
        return my_session.query(Status).filter(Status.time.between(start, end)).all()

    @load_session
    def insert_status(my_session: Session, status_code: int):
        """Insert status.

        :param my_session: Current session.
        :type my_session: Session.
        :param status_code: Code representing current status.
        :type status_code: int.
        """
        new_status = Status(status=status_code)
        my_session.add(new_status)
        my_session.commit()
        return new_status

    @load_session
    def get_unpushed_notices(my_session: Session) -> List[Notification]:
        return my_session.query(Notification).options(joinedload('attachments')).filter(Notification.is_pushed.is_(False)).all()

    @load_session
    def mark_pushed(my_session: Session, notice_id: Notification):
        old_notice = my_session.query(Notification).filter(Notification.id == notice_id).one_or_none()
        if old_notice is None:
            logging.warning(f"SQLHandler: Duplicate push of Notification `{old_notice}`.")
        else:
            old_notice.is_pushed = True
            my_session.commit()

    @load_session
    def toggle_insider(my_session: Session, chat_id: int) -> Union[None, bool]:
        chat = my_session.query(Chat).filter(Chat.id == chat_id).one_or_none()
        if chat is None:
            logging.warning(f"SQLHandler: No such chat `{chat_id}`.")
            return None
        else:
            chat.is_insider = not chat.is_insider
            my_session.commit()
            return chat.is_insider
