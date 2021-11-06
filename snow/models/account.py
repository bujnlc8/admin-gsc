# coding=utf-8

from __future__ import unicode_literals

from sqlalchemy.dialects.mysql import INTEGER, TINYINT, VARCHAR

from snow.ext import db


class Account(db.Model):

    __tablename__ = 'account'

    id_ = db.Column(
        'id', INTEGER(display_width=11),
        nullable=False, primary_key=True, doc='')
    user_name = db.Column(
        'user_name',
        VARCHAR(
            charset=u'utf8mb4', collation=u'utf8mb4_bin', length=32),
        nullable=False, doc='')
    password = db.Column(
        'password',
        VARCHAR(
            charset=u'utf8mb4', collation=u'utf8mb4_bin', length=128),
        nullable=False, doc='')
    role = db.Column(
        'role', TINYINT(display_width=1),
        nullable=True, doc='', server_default='0')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id_

    def __unicode__(self):
        return self.user_name
