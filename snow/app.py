# coding=utf-8

import json
import os

import flask_login as login
from flask import Flask, redirect, url_for
from flask_admin import Admin
from werkzeug.utils import import_string

from snow.ext import db, redis
from snow.views.index import IndexView

modelviews = [
    'snow.views.index.account_view',
    'snow.views.gsc.gsc_view',
    'snow.views.question.question_view',
    'snow.views.feedback.feedback_view',
    'snow.views.question.region_view',
    'snow.views.gsc.quotes_view',
]

extensions = ['snow.ext.db']

login_manager = login.LoginManager()


def create_app():
    app = Flask('snow')
    app.config['DEBUG'] = os.environ.get('SNOW_DEBUG', 'false') == 'true'
    app.config['TESTING'] = os.environ.get('SNOW_TESTING', 'false') == 'true'
    app.config['SERVER_NAME'] = os.environ.get('SNOW_SERVER_NAME')
    app.config['SECRET_KEY'] = os.environ.get('SNOW_SECRET_KEY')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SNOW_SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_BINDS'] = json.loads(os.environ.get('SNOW_SQLALCHEMY_BINDS'))
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 1440
    app.config['SQLALCHEMY_POOL_SIZE'] = 100
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 5
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 5
    app.config['REDIS_URL'] = os.environ.get('SNOW_REDIS_URL')
    admin = Admin(
        app,
        name='📚',
        template_mode='bootstrap4',
        base_template='base.html',
        index_view=IndexView(url='/', name=''),
    )
    login_manager.init_app(app)
    redis.init_app(app)
    for extension in extensions:
        ext = import_string(extension)
        ext.init_app(app)
    for modelview_qualname in modelviews:
        modelview = import_string(modelview_qualname)
        admin.add_view(modelview)
    # 处理403
    app.register_error_handler(403, handle_403)
    return app


@login_manager.user_loader
def load_user(user_id):
    from snow.models.account import Account

    return db.session.query(Account).get(user_id)


def handle_403(e):
    return redirect(url_for('admin.index'))
