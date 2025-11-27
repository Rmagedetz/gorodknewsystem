import pandas as pd
from sqlalchemy import (Column, Integer, String, Date, Float, create_engine, ForeignKey, func, Boolean, case,
                        UniqueConstraint, DateTime, Text, distinct, text, DECIMAL, BIGINT)
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
            season = session.query(cls).filter_by(**parameters).first()
            if not season:
                raise ValueError("Сезон не найден")

            # Проверяем наличие филиалов
            filial_exists = session.query(Filials).filter_by(season_name=season.season_name).first()
            if filial_exists:
                raise ValueError("Нельзя удалить сезон, в котором есть филиалы")

            session.delete(season)

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
            filial = session.query(cls).filter_by(**parameters).first()
            if not filial:
                raise ValueError("Филиал не найден")

            # Проверяем наличие групп
            group_exists = session.query(Groups).filter_by(
                season_name=filial.season_name,
                filial_name=filial.filial_name
            ).first()

            if group_exists:
                raise ValueError("Нельзя удалить филиал, в котором есть группы")

            session.delete(filial)

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
    days = Column(Integer)
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
            # Ищем группу
            group = session.query(cls).filter_by(**parameters).first()
            if not group:
                raise ValueError("Группа не найдена")

            # Проверяем наличие детей (записей) через таблицу Records
            record_exists = session.query(Records).filter_by(
                season_name=group.season_name,
                filial_name=group.filial_name,
                group_name=group.group_name
            ).first()

            if record_exists:
                raise ValueError("Нельзя удалить группу, в которой есть записи детей")

            # Удаляем группу
            session.delete(group)

    @classmethod
    def edit_record(cls, season_name, filial_name, group_name, **parameters):
        with session_scope() as session:
            session.query(cls).filter_by(season_name=season_name,
                                         filial_name=filial_name,
                                         group_name=group_name).update(parameters)

    @classmethod
    def get_filial_for_group_in_season(cls, season_name, group_name):
        with session_scope() as session:
            group = session.query(cls).filter_by(season_name=season_name,
                                                 group_name=group_name).first()
            return group.filial_name

    @classmethod
    def get_days_for_group_in_season(cls, season_name, group_name):
        with session_scope() as session:
            group = session.query(cls).filter_by(season_name=season_name,
                                                 group_name=group_name).first()
            return group.days

    @classmethod
    def rename_group(cls, season_name, filial_name, group_name, new_group_name):
        with session_scope() as session:
            session.query(cls).filter_by(season_name=season_name,
                                         filial_name=filial_name,
                                         group_name=group_name).update({"group_name": new_group_name})

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

                # 🔹 Сортировка по group_id (или любому автоинкрементному PK) для детерминированного порядка
                if hasattr(cls, 'group_id'):
                    query = query.order_by(cls.group_id)

                data = query.all()
                obj_df = pd.DataFrame.from_records(data, columns=columns)
                obj_df.index += 1
                return obj_df
            except:
                return pd.DataFrame()

    @classmethod
    def get_start_end(cls, season, filial, group):
        with session_scope() as session:
            group = session.query(cls).filter_by(season_name=season,
                                                 filial_name=filial,
                                                 group_name=group).first()
            return {'start_date': group.start_date,
                    'end_date': group.end_date}


class Records(Base):
    __tablename__ = "records"

    record_id = Column(Integer, primary_key=True)

    season_name = Column(String(100), nullable=False)
    filial_name = Column(String(100), nullable=False)
    child_name = Column(String(100), nullable=False)
    parent_name = Column(String(100), nullable=False)
    group_name = Column(String(100), nullable=False)
    record_status = Column(String(10), nullable=False)
    comment = Column(Text, nullable=False)

    __table_args__ = (
        # нельзя дублировать одного ребёнка в той же группе/филиале/сезоне
        UniqueConstraint(
            "season_name",
            "filial_name",
            "group_name",
            "child_name",
            name="uix_child_group_unique",
        ),
        # нельзя у одного родителя иметь двух детей с одинаковым именем
        UniqueConstraint(
            "parent_name",
            "child_name",
            name="uix_parent_child_unique",
        ),
        # нельзя дублировать один и тот же статус
        # у того же ребёнка того же родителя в том же сезоне/филиале/группе
        UniqueConstraint(
            "season_name",
            "filial_name",
            "group_name",
            "parent_name",
            "child_name",
            "record_status",
            name="uix_record_status_unique",
        ),
    )

    @classmethod
    def update_record_status(cls, season_name, filial_name, group_name,
                             child_name, parent_name):
        with session_scope() as session:
            session.query(cls).filter_by(season_name=season_name,
                                         filial_name=filial_name,
                                         group_name=group_name,
                                         child_name=child_name,
                                         parent_name=parent_name).update({"record_status": "1о"})

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
    def rename_group(cls, season_name, filial_name, group_name, new_group_name):
        with session_scope() as session:
            session.query(cls).filter_by(season_name=season_name,
                                         filial_name=filial_name,
                                         group_name=group_name).update({"group_name": new_group_name})

    @classmethod
    def rename_child(cls, parent_name, old_child_name, new_child_name):
        with session_scope() as session:
            session.query(cls).filter_by(parent_name=parent_name,
                                         child_name=old_child_name
                                         ).update({"child_name": new_child_name})

    @classmethod
    def rename_parent(cls, child_name, old_parent_name, new_parent_name):
        with session_scope() as session:
            session.query(cls).filter_by(child_name=child_name,
                                         parent_name=old_parent_name
                                         ).update({'parent_name': new_parent_name})

    @classmethod
    def get_unique_parents(cls, **filters):
        with session_scope() as session:
            query = session.query(distinct(cls.parent_name))
            if filters:
                query = query.filter_by(**filters)
            return [row[0] for row in query.all()]

    @classmethod
    def get_children_for_parent(cls, parent_name, **filters):
        with session_scope() as session:
            q = session.query(distinct(cls.child_name)).filter_by(parent_name=parent_name, **filters)
            return [row[0] for row in q.all()]

    @classmethod
    def get_parent_for_child(cls, child_name, **filters):
        with session_scope() as session:
            q = session.query(distinct(cls.parent_name)).filter_by(child_name=child_name, **filters)
            return [row[0] for row in q.all()]

    @classmethod
    def get_all_unique_children(cls, **filters):
        with session_scope() as session:
            q = session.query(distinct(cls.child_name))
            if filters:
                q = q.filter_by(**filters)
            return [row[0] for row in q.all()]


class Child(Base):
    __tablename__ = 'children'

    # базовые данные
    id = Column(Integer, primary_key=True)
    child_name = Column(String(50), nullable=False)
    parent_name = Column(String(50), nullable=False)
    child_age = Column(Integer, nullable=False)

    # анкетные данные
    child_birthday = Column(Date, nullable=True, default=None)
    parent_add = Column(String(50), nullable=True, default="")
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
    oms = Column(String(20), nullable=True, default="")

    __table_args__ = (
        UniqueConstraint('child_name', 'parent_name', name='uix_child_parent_name'),
    )

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

    @classmethod
    def rename_child(cls, parent_name, old_child_name, new_child_name):
        with session_scope() as session:
            session.query(cls).filter_by(parent_name=parent_name,
                                         child_name=old_child_name
                                         ).update({"child_name": new_child_name})

    @classmethod
    def rename_parent(cls, child_name, old_parent_name, new_parent_name):
        with session_scope() as session:
            session.query(cls).filter_by(child_name=child_name,
                                         parent_name=old_parent_name
                                         ).update({'parent_name': new_parent_name})

    @classmethod
    def attach_anket_to_child(cls, child_name, parent_name, anket_df):
        # Берем первую строку DataFrame
        row_data = anket_df.iloc[0].to_dict()

        # Переименовываем колонки, если нужно
        if 'name' in row_data:
            row_data['child_name'] = row_data.pop('name')

        with session_scope() as session:
            obj = session.query(cls).filter_by(child_name=child_name, parent_name=parent_name).first()
            if obj:
                for key, value in row_data.items():
                    setattr(obj, key, value)


class Parent(Base):
    __tablename__ = 'parents'
    id = Column(Integer, primary_key=True)
    parent_name = Column(String(50), nullable=False, unique=True)
    parent_phone = Column(String(50), nullable=False)
    email = Column(String(100), nullable=True, default="")

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

    @classmethod
    def rename_parent(cls, old_parent_name, new_parent_name):
        with session_scope() as session:
            session.query(cls).filter_by(parent_name=old_parent_name
                                         ).update({'parent_name': new_parent_name})

    @classmethod
    def attach_anket_to_parent(cls, parent_name, anket_df):
        with session_scope() as session:
            session.query(cls).filter_by(parent_name=parent_name
                                         ).update({'parent_name': anket_df['parent_main_name'][0],
                                                   'parent_phone': anket_df['parent_main_phone'][0],
                                                   'email': anket_df['email'][0]})


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
    def batch_add(cls, data):
        # если data — DataFrame, превращаем в список словарей
        if isinstance(data, pd.DataFrame):
            records = data.to_dict(orient="records")
        else:
            records = data  # предполагаем, что это уже список словарей

        with session_scope() as session:
            session.query(cls).delete()
            session.execute(text(f"ALTER TABLE {cls.__table__.name} AUTO_INCREMENT = 1"))
            session.bulk_insert_mappings(cls, records)
            session.commit()

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


class Payments_forms(Base):
    __tablename__ = "payment_forms"
    id = Column(Integer, primary_key=True)
    form = Column(String(100), nullable=False, unique=True)

    @classmethod
    def add_object(cls, **parameters):
        with session_scope() as session:
            add = cls(**parameters)
            session.add(add)

    @classmethod
    def delete_record(cls, **parameters):
        with session_scope() as session:
            record = session.query(cls).filter_by(**parameters).first()
            session.delete(record)

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


class Payment_options(Base):
    __tablename__ = "payment_options"
    id = Column(Integer, primary_key=True)
    option = Column(String(100), nullable=False, unique=True)

    @classmethod
    def add_object(cls, **parameters):
        with session_scope() as session:
            add = cls(**parameters)
            session.add(add)

    @classmethod
    def delete_record(cls, **parameters):
        with session_scope() as session:
            record = session.query(cls).filter_by(**parameters).first()
            session.delete(record)

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


class Payments(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    account = Column(String(100), nullable=False)
    season_name = Column(String(100), nullable=False)
    group_name = Column(String(100), nullable=False)
    child_name = Column(String(100), nullable=False)
    parent_name = Column(String(100), nullable=False)
    pay_form = Column(String(100), nullable=False)
    pay_sum = Column(DECIMAL, nullable=False)
    option = Column(String(100), nullable=False)
    comment = Column(String(100), nullable=False)

    @classmethod
    def add_object(cls, **parameters):
        with session_scope() as session:
            add = cls(**parameters)
            session.add(add)

    @classmethod
    def delete_record(cls, **parameters):
        with session_scope() as session:
            record = session.query(cls).filter_by(**parameters).first()
            session.delete(record)

    @classmethod
    def edit_record(cls, pay_id, **parameters):
        with session_scope() as session:
            session.query(cls).filter_by(id=pay_id).update(parameters)

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


class Payments_from_balance(Base):
    __tablename__ = "payments_from_balance"
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    account = Column(String(100), nullable=False)
    season_name = Column(String(100), nullable=False)
    group_name = Column(String(100), nullable=False)
    child_name = Column(String(100), nullable=False)
    parent_name = Column(String(100), nullable=False)
    pay_form = Column(String(100), nullable=False)
    pay_sum = Column(DECIMAL, nullable=False)
    option = Column(String(100), nullable=False)
    comment = Column(String(100), nullable=False)

    @classmethod
    def add_object(cls, **parameters):
        with session_scope() as session:
            add = cls(**parameters)
            session.add(add)

    @classmethod
    def delete_record(cls, **parameters):
        with session_scope() as session:
            record = session.query(cls).filter_by(**parameters).first()
            session.delete(record)

    @classmethod
    def edit_record(cls, pay_id, **parameters):
        with session_scope() as session:
            session.query(cls).filter_by(id=pay_id).update(parameters)

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


class Visits(Base):
    __tablename__ = 'visits'

    visit_id = Column(Integer, primary_key=True)

    season_name = Column(String(100), nullable=False)
    filial_name = Column(String(100), nullable=False)
    child_name = Column(String(100), nullable=False)
    parent_name = Column(String(100), nullable=False)
    group_name = Column(String(100), nullable=False)
    day_number = Column(Integer, nullable=False)
    visit_status = Column(String(10), nullable=False)

    UniqueConstraint(
        "season_name",
        "filial_name",
        "group_name",
        "parent_name",
        "child_name",
        "day_number",
        "visit_status",
        name="uix_record_status_unique",
    )

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


class Debits(Base):
    __tablename__ = 'debits'
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    account = Column(String(100), nullable=False)
    season_name = Column(String(100), nullable=False)
    filial_name = Column(String(100), nullable=False)
    group_name = Column(String(100), nullable=False)
    child_name = Column(String(100), nullable=False)
    parent_name = Column(String(100), nullable=False)
    pay_sum = Column(DECIMAL, nullable=False)
    pay_form = Column(String(100), nullable=False)
    option = Column(String(100), nullable=False)
    comment = Column(String(100), nullable=False)

    @classmethod
    def add_object(cls, **parameters):
        with session_scope() as session:
            add = cls(**parameters)
            session.add(add)

    @classmethod
    def edit_record(cls, pay_id, **parameters):
        with session_scope() as session:
            session.query(cls).filter_by(id=pay_id).update(parameters)

    @classmethod
    def delete_record(cls, **parameters):
        with session_scope() as session:
            record = session.query(cls).filter_by(**parameters).first()
            session.delete(record)

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


class Bot_subscribers(Base):
    __tablename__ = 'bot_subscribers'
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)

    subscriber_tg_id = Column(BIGINT, nullable=False)
    subscriber_tg_first_name = Column(String(100))
    subscriber_tg_last_name = Column(String(100))
    subscriber_tg_username = Column(String(100))

    present_accepted = Column(Boolean)

    subscriber_real_first_name = Column(String(100))
    subscriber_real_last_name = Column(String(100))
    subscriber_real_username = Column(String(100))

    subscriber_child_name = Column(String(100))
    subscriber_child_birthday = Column(Date)

    __table_args__ = (
        UniqueConstraint('subscriber_tg_id', 'subscriber_child_name', name='_tg_child_uc'),
    )

    @classmethod
    def add_object(cls, **parameters):
        with session_scope() as session:
            add = cls(**parameters)
            session.add(add)

    @classmethod
    def delete_record(cls, **parameters):
        with session_scope() as session:
            record = session.query(cls).filter_by(**parameters).first()
            session.delete(record)

    @classmethod
    def edit_record(cls, tg_id, **parameters):
        with session_scope() as session:
            session.query(cls).filter_by(subscriber_tg_id=tg_id).update(parameters)

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
