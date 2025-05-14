import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Promocode(SqlAlchemyBase):
    __tablename__ = 'promocodes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    promocode = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    action = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    used_count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    # data_end = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
