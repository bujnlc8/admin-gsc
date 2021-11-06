# coding=utf-8

import flask_login as login
from flask import redirect, request, url_for
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import fields, form, validators

from snow.ext import db
from snow.models.account import Account


class LoginForm(form.Form):
    user_name = fields.StringField(
        validators=[validators.required()], label='用户名:')
    password = fields.PasswordField(
        validators=[validators.required()], label='密码:')

    def validate(self):
        user = self.get_user()
        if user is None:
            raise validators.ValidationError('Invalid user')

        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError('Invalid password')
        login.login_user(user)
        return True

    def get_user(self):
        return db.session.query(Account).filter_by(user_name=self.user_name.data).first()


class RegistrationForm(form.Form):
    user_name = fields.StringField(
        validators=[validators.required()], label='用户名:')
    password = fields.PasswordField(
        validators=[validators.required()], label='密码:')

    def validate(self):
        if db.session.query(Account).filter_by(user_name=self.user_name.data).count() > 0:
            raise validators.ValidationError('Duplicate username')
        return True


class IndexView(AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return redirect(url_for('gsc.index_view'))

    @expose('/login', methods=('GET', 'POST'))
    def login_view(self):
        form = LoginForm(request.form)
        if request.method.upper() == 'POST' and form.validate() and login.current_user.is_authenticated:
            return redirect(url_for('gsc.index_view'))
        link = '<p>Don\'t have an account? <a href="' + \
            url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(IndexView, self).index()

    @expose('/register', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if request.method.upper() == 'POST' and form.validate():
            user = Account()
            form.populate_obj(user)
            user.password = generate_password_hash(form.password.data)
            db.session.add(user)
            db.session.commit()
            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + \
            url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(IndexView, self).index()

    @expose('/logout')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))

    def is_visible(self):
        return False


class AccountModelView(ModelView):

    def is_accessible(self):
        return (login.current_user.is_authenticated and login.current_user.role & 1 and login.current_user.role & 2 and
                login.current_user.role & 4)


account_view = AccountModelView(Account, db.session, name='用户管理')
