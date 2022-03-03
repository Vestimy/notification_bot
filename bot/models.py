from sqlalchemy import String, INTEGER, DATE, and_, or_
from db import Base, db_session
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Date, Column, Integer, \
    String, ForeignKey, FLOAT, BIGINT, Text, TEXT

from datetime import datetime, timedelta, date
from paginate_sqlalchemy import SqlalchemyOrmPage
import logging

logging.basicConfig(filename="error.log", format='%(levelname)s %(asctime)s - %(message)s', level=logging.INFO)


class Month(Base):
    __tablename__ = 'month'
    id = Column(INTEGER, primary_key=True)
    title = Column(String(100))

    schedule = relationship('Schedule', back_populates='month')

    def __repr__(self):
        return self.title

    @staticmethod
    def exists(title):
        return Month.query.filter(Month.title == title).first()

    @staticmethod
    def set_moth(title):
        result = Month(title=title)
        db_session.add(result)
        db_session.commit()

    @staticmethod
    def add_base(result):
        try:
            db_session.add(result)
            db_session.commit()
        except Exception as e:
            logging.error(e)


class Schedule(Base):
    __tablename__ = 'schedule'

    id = Column(INTEGER, primary_key=True)
    first_str = Column(String(100))

    km = Column(String(250))
    date = Column(Date)
    city = Column(String(100))
    artist = Column(String(100))
    playground = Column(String(100))
    executor = Column(String(100))
    note = Column(String(100))
    manager = Column(String(100))

    check = Column(Boolean)

    month_id = Column(INTEGER, ForeignKey('month.id'))
    # quipmentcategory = relationship('EquipmentCategory', back_populates='equipmentsubcategory')
    month = relationship('Month', back_populates='schedule')

    # def __init__(self, **kwargs):
    #     self.km = kwargs.get('km')
    #     self.date = kwargs.get('date')
    #     self.city = kwargs.get('city')
    #     self.artist = kwargs.get('artist')
    #     self.playground = kwargs.get('playground')
    #     self.executor = kwargs.get('executor')
    #     self.note = kwargs.get('note')
    #     self.manager = kwargs.get('manager')
    #     self.month_id = kwargs.get('month_id')
    #     self.first_str = kwargs.get('first_str')
    #     self.check = kwargs.get('check')

    @staticmethod
    def get_executors(name):
        names = Schedule.query.all()
        for i in names:
            if name in i.executor:
                return True

    @staticmethod
    def get_by_number_of_days(days):
        filter_day = date.today() + timedelta(days=days)
        return Schedule.query.filter(and_(Schedule.date <= filter_day, Schedule.date >= date.today())).filter(
            and_(Schedule.city != '', Schedule.artist != '')).all()

    @staticmethod
    def set_data(data_sheet):
        db_session.add_all(data_sheet)
        db_session.commit()

    #
    def __repr__(self):
        return self.date.strftime("%d.%m.%Y")


class Executors(Base):
    __tablename__ = 'executors'
    id = Column(INTEGER, primary_key=True)
    alias = Column(String(50))
    first_name = Column(String(100))
    last_name = Column(String(100))
    chat_id = Column(BIGINT)


class Users(Base):
    __tablename__ = 'users'
    id = Column(INTEGER, primary_key=True)
    user_id = Column(BIGINT, unique=True, nullable=False)
    first_name = Column(String(60))
    last_name = Column(String(60))
    alias = Column(String(15))
    signup = Column(String(60), default='first_name')
    newsletter = Column(Boolean, default=False)

    @staticmethod
    def user_exists(user_id):
        user = Users.query.filter(Users.user_id == user_id).first()
        return user

    @staticmethod
    def set_new_user(user_id, first_name, last_name, alias, newslatter):
        user = Users()
        user.user_id = user_id
        user.first_name = first_name
        user.last_name = last_name
        user.alias = alias
        user.newsletter = newslatter
        db_session.add(user)
        db_session.commit()

    @staticmethod
    def add_user(user_id):
        user = Users(user_id=user_id)
        db_session.add(user)
        db_session.commit()

    @staticmethod
    def set_first_name(user_id, first_name):
        user = Users.query.filter(Users.user_id == user_id).first()
        user.first_name = first_name
        db_session.commit()

    @staticmethod
    def set_last_name(user_id, last_name):
        user = Users.query.filter(Users.user_id == user_id).first()
        user.last_name = last_name
        db_session.commit()

    @staticmethod
    def set_alias(user_id, alias):
        user = Users.query.filter(Users.user_id == user_id).first()
        user.alias = alias
        db_session.commit()

    @staticmethod
    def set_newsletter(user_id, newsletter):
        user = Users.query.filter(Users.user_id == user_id).first()
        user.newsletter = newsletter
        db_session.commit()

    @staticmethod
    def get_signup(user_id):
        user = Users.query.filter(Users.user_id == user_id).first()
        if user:
            return user.signup

    @staticmethod
    def set_signup(user_id, signup):
        user = Users.query.filter(Users.user_id == user_id).first()
        user.signup = signup
        db_session.commit()

    @staticmethod
    def get_exists_alias(alias):
        aliass = Schedule.query.all()
        for i in aliass:
            if alias in i.executor.split():
                return True

        return False
        # if Users.query.filter(Users.alias == alias).first():
        #     return True
        # else:
        #     return False

    @staticmethod
    def get_all_nesletter():
        users = Users.query.filter(Users.newsletter == True).all()
        return users

    @staticmethod
    def get_user_alias_for_last_name(alias_last_name):
        users = Users.query.filter(Users.last_name == alias_last_name).first()
        return users


class ConcertHall(Base):
    __tablename__ = 'concerthall'

    id = Column(INTEGER, primary_key=True)
    city = Column(String(100))
    title = Column(String(100))
    adress = Column(String(100))
    note = Column(Text)
    contact_person = Column(Text)
    url = Column(String(100))

    def __repr__(self):
        return self.title

    @staticmethod
    def get_first_row(data):
        return ConcertHall.query.filter(ConcertHall.city == data).first()

    @staticmethod
    def get_all_hall():
        return ConcertHall.query.order_by(ConcertHall.title.asc()).all()

    @staticmethod
    def get_one_hall(id):
        return ConcertHall.query.get(id)

    @staticmethod
    def get_paginate_all(page=None, page_count=20):
        query = ConcertHall.query.order_by(ConcertHall.title.asc())
        if page is None:
            result = SqlalchemyOrmPage(query, items_per_page=page_count)
            return result
        result = SqlalchemyOrmPage(query, items_per_page=page_count, page=page)
        return result
