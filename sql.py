import pandas as pd
from sqlalchemy import (Column, Integer, String, Date, Float, create_engine, ForeignKey, func, Boolean, case,
                        UniqueConstraint, DateTime, Text)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, aliased, joinedload
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager
from connections import sql_connection_string
from datetime import datetime

engine = create_engine(sql_connection_string)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_list(cls, field_name):
    with session_scope() as session:
        field = getattr(cls, field_name)
        results = session.query(field).all()
        result_list = [getattr(result, field_name) for result in results]
    return result_list


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)

    editing_users = Column(Boolean, nullable=False)
    editing_seasons = Column(Boolean, nullable=False)
    editing_filials = Column(Boolean, nullable=False)
    editing_groups = Column(Boolean, nullable=False)
    editing_records = Column(Boolean, nullable=False)
    editing_payments = Column(Boolean, nullable=False)
    editing_visits = Column(Boolean, nullable=False)

    @classmethod
    def check_user_password(cls, username):
        with session_scope() as session:
            result = session.query(cls.password).filter_by(user_name=username).first()
            return result[0] if result else None

    @classmethod
    def get_user_list_for_login(cls):
        user_list = get_list(cls, "user_name")
        return user_list

    @classmethod
    def add_record(cls, **parameters):
        with session_scope() as session:
            add = cls(**parameters)
            session.add(add)

    @classmethod
    def delete_record(cls, **parameters):
        with session_scope() as session:
            record = session.query(cls).filter_by(**parameters).first()
            session.delete(record)

    @classmethod
    def edit_record(cls, name, **parameters):
        with session_scope() as session:
            session.query(cls).filter_by(user_name=name).update(parameters)

    @classmethod
    def get_df(cls, **parameters):
        with session_scope() as session:
            try:
                columns = [c.name for c in cls.__table__.columns]
                query = session.query(*[getattr(cls, col) for col in columns]).filter_by(**parameters)
                data = query.all()
                obj_df = pd.DataFrame.from_records(data, columns=columns)
                obj_df.index += 1
                return obj_df
            except:
                return pd.DataFrame()


class Seasons(Base):
    __tablename__ = "seasons"

    season_id = Column(Integer, primary_key=True)

    season_name = Column(String(100), nullable=False, unique=True)
    start_date = Column(Date)
    end_date = Column(Date)

    @classmethod
    def add_record(cls, **parameters):
        with session_scope() as session:
            add = cls(**parameters)
            session.add(add)

    @classmethod
    def delete_record(cls, **parameters):
        with session_scope() as session:
            record = session.query(cls).filter_by(**parameters).first()
            session.delete(record)

    @classmethod
    def edit_record(cls, name, **parameters):
        with session_scope() as session:
            session.query(cls).filter_by(season_name=name).update(parameters)

    @classmethod
    def get_df(cls, **parameters):
        with session_scope() as session:
            try:
                columns = [c.name for c in cls.__table__.columns]
                query = session.query(*[getattr(cls, col) for col in columns]).filter_by(**parameters)
                data = query.all()
                obj_df = pd.DataFrame.from_records(data, columns=columns)
                obj_df.index += 1
                return obj_df
            except:
                return pd.DataFrame()


class Filials(Base):
    __tablename__ = 'filials'

    filial_id = Column(Integer, primary_key=True)
    season_name = Column(String(100), nullable=False)
    filial_name = Column(String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint('season_name', 'filial_name', name='uix_season_filial_name'),
    )

    @classmethod
    def add_record(cls, **parameters):
        with session_scope() as session:
            add = cls(**parameters)
            session.add(add)

    @classmethod
    def delete_record(cls, **parameters):
        with session_scope() as session:
            record = session.query(cls).filter_by(**parameters).first()
            session.delete(record)

    @classmethod
    def rename_season(cls, old_season_name, new_season_name):
        with session_scope() as session:
            session.query(cls).filter_by(season_name=old_season_name).update({"season_name": new_season_name})

    @classmethod
    def rename_filial(cls, season_name, filial_name, new_filial_name):
        with session_scope() as session:
            session.query(cls).filter_by(season_name=season_name,
                                         filial_name=filial_name).update({"filial_name": new_filial_name})

    @classmethod
    def get_df(cls, **parameters):
        with session_scope() as session:
            try:
                columns = [c.name for c in cls.__table__.columns]
                query = session.query(*[getattr(cls, col) for col in columns]).filter_by(**parameters)
                data = query.all()
                obj_df = pd.DataFrame.from_records(data, columns=columns)
                obj_df.index += 1
                return obj_df
            except:
                return pd.DataFrame()


class Groups(Base):
    __tablename__ = "groups"

    group_id = Column(Integer, primary_key=True)
    season_name = Column(String(100), nullable=False)
    filial_name = Column(String(100), nullable=False)
    group_name = Column(String(100), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    capacity = Column(Integer)

    __table_args__ = (
        UniqueConstraint('season_name', 'group_name', name='uix_season_filial_name'),
    )

    @classmethod
    def add_record(cls, **parameters):
        with session_scope() as session:
            add = cls(**parameters)
            session.add(add)

    @classmethod
    def delete_record(cls, **parameters):
        with session_scope() as session:
            record = session.query(cls).filter_by(**parameters).first()
            session.delete(record)

    @classmethod
    def edit_record(cls, season_name, filial_name, group_name, **parameters):
        with session_scope() as session:
            session.query(cls).filter_by(season_name=season_name,
                                         filial_name=filial_name,
                                         group_name=group_name).update(parameters)

    @classmethod
    def rename_season(cls, old_season_name, new_season_name):
        with session_scope() as session:
            session.query(cls).filter_by(season_name=old_season_name).update({"season_name": new_season_name})

    @classmethod
    def rename_filial(cls, season_name, filial_name, new_filial_name):
        with session_scope() as session:
            session.query(cls).filter_by(season_name=season_name,
                                         filial_name=filial_name).update({"filial_name": new_filial_name})

    @classmethod
    def get_df(cls, **parameters):
        with session_scope() as session:
            try:
                columns = [c.name for c in cls.__table__.columns]
                query = session.query(*[getattr(cls, col) for col in columns]).filter_by(**parameters)
                data = query.all()
                obj_df = pd.DataFrame.from_records(data, columns=columns)
                obj_df.index += 1
                return obj_df
            except:
                return pd.DataFrame()


class Records(Base):
    __tablename__ = "records"

    record_id = Column(Integer, primary_key=True)

    # новые общие поля
    child_name = Column(String(100), nullable=False)
    parent_name = Column(String(100))
    group_name = Column(String(100), nullable=False)
    record_status = Column(String(10), nullable=False)

    # уникальность: одному ребенку одного родителя в одной группе — только один статус
    __table_args__ = (
        UniqueConstraint("child_name", "parent_name", "group_name", name="uix_child_parent_group"),
    )

    @classmethod
    def get_children_for_parent(cls, parent_name: str):
        """Возвращает список уникальных child_name для указанного parent_name"""
        with session_scope() as session:
            result = session.query(cls.child_name).filter_by(parent_name=parent_name).distinct().all()
            # .all() возвращает список кортежей, распакуем
            return [r[0] for r in result]

    @classmethod
    def add_object(cls, **parameters):
        with session_scope() as session:
            add = cls(**parameters)
            session.add(add)

    @classmethod
    def get_df(cls, **parameters):
        with session_scope() as session:
            try:
                columns = [c.name for c in cls.__table__.columns]
                query = session.query(*[getattr(cls, col) for col in columns]).filter_by(**parameters)
                data = query.all()
                obj_df = pd.DataFrame.from_records(data, columns=columns)
                obj_df.index += 1
                return obj_df
            except:
                return pd.DataFrame()


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
