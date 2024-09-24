# coding=utf-8

from __future__ import unicode_literals

from sqlalchemy.dialects.mysql import VARCHAR, INTEGER

from snow.ext import db


class Quotes(db.Model):
    __bind_key__ = 'challenge'

    __tablename__ = 'quotes'

    id_ = db.Column('id', INTEGER(display_width=11), nullable=False, primary_key=True, doc='')
    quote = db.Column('quote', VARCHAR(charset='utf8mb4', collation='utf8mb4_bin', length=128), nullable=False, doc='')
    author = db.Column('author', VARCHAR(charset='utf8mb4', collation='utf8mb4_bin', length=32), nullable=False, doc='')
