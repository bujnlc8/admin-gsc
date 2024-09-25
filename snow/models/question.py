# coding=utf-8

from __future__ import unicode_literals

from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, DATETIME
from snow.ext import db


class Question(db.Model):
    __bind_key__ = 'challenge'

    __tablename__ = 'question'

    id_ = db.Column('id', INTEGER(display_width=11), nullable=False, primary_key=True, doc='')
    content = db.Column(
        'content', VARCHAR(charset='utf8mb4', collation='utf8mb4_bin', length=5000), nullable=False, doc=''
    )
    options = db.Column(
        'options', VARCHAR(charset='utf8mb4', collation='utf8mb4_bin', length=2000), nullable=False, doc=''
    )
    analysis = db.Column(
        'analysis', VARCHAR(charset='utf8mb4', collation='utf8mb4_bin', length=5000), nullable=False, doc=''
    )
    answer = db.Column('answer', INTEGER(display_width=1), nullable=False, doc='')
    level = db.Column('level', INTEGER(display_width=1), nullable=False, doc='')
    category = db.Column('category', INTEGER(display_width=1), nullable=False, doc='')
    status = db.Column('status', INTEGER(display_width=1), nullable=False, doc='')
    create_time = db.Column('create_time', DATETIME())
    update_time = db.Column('update_time', DATETIME())
