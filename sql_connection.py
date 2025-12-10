from sqlalchemy import (Column, Integer, String, Date, create_engine, Text)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager

db_user = 'tilda_forms_adder'
db_password = 'Vttnthrnvtm_T'
db_host = '91.193.182.16'
db_port = "3310"
db_name = 'g_db_3'


sql_connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(sql_connection_string)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Ankets(Base):
    __tablename__ = 'ankets'

    id = Column(Integer, primary_key=True)
    email = Column(String(100), nullable=True, default="")
    name = Column(String(50), nullable=False)
    child_birthday = Column(Date, nullable=True, default=None)
    parent_main_name = Column(String(50), nullable=False)
    parent_main_phone = Column(String(50), nullable=False)
    parent_add = Column(Text, nullable=True, default="")
    phone_add = Column(String(20), nullable=True, default="")
    leave = Column(String(10), nullable=True, default="")
    additional_contact = Column(Text, nullable=True, default="")
    addr = Column(String(200), nullable=True, default="")
    disease = Column(Text, nullable=True, default="")
    allergy = Column(Text, nullable=True, default="")
    other = Column(Text, nullable=True, default="")
    physic = Column(Text, nullable=True, default="")
    swimm = Column(String(10), nullable=True, default="")
    jacket_swimm = Column(String(10), nullable=True, default="")
    hobby = Column(Text, nullable=True, default="")
    school = Column(String(100), nullable=True, default="")
    additional_info = Column(Text, nullable=True, default="")
    departures = Column(String(10), nullable=True, default="")
    referer = Column(String(300), nullable=True, default="")
    ok = Column(String(10), nullable=True, default="")
    mailing = Column(Text, nullable=True, default="")
    personal_accept = Column(String(10), nullable=True, default="")
    oms = Column(Text, nullable=True, default="")

    @classmethod
    def add_object(cls, **parameters):
        with session_scope() as session:
            add = cls(**parameters)
            session.add(add)


Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    finally:
        db.close()
