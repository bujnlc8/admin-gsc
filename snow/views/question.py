# coding=utf-8
import flask_login as login
from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup
from wtforms import fields, validators

from datetime import datetime

from snow.ext import db, redis

from snow.models.question import Question

CATEGORY = [(1, '常识'), (2, '百科'), (3, '历史'), (4, '地理'), (5, '生活'), (6, '体育'), (7, '法规'), (8, '诗词')]

LEVEL = [(1, '简单'), (2, '中等'), (3, '困难')]

STATUS = [(1, '正常'), (0, '删除')]


class QuestionView(ModelView):

    page_size = 12

    def is_accessible(self):
        return login.current_user.is_authenticated and (login.current_user.role & 8)

    @property
    def can_create(self):
        return self.is_accessible() and (login.current_user.role & 16)

    @property
    def can_edit(self):
        return self.is_accessible() and (login.current_user.role & 32)

    @property
    def can_delete(self):
        return self.is_accessible() and (login.current_user.role & 64)

    column_sortable_list = ('id_', )

    column_labels = {
        'id_': 'ID',
        'content': '题目',
        'options': '选项',
        'answer': '答案',
        'level': '难度',
        'category': '分类',
        'status': '状态',
        'create_time': '创建时间',
        'update_time': '更新时间',
    }

    column_list = ('id_', 'content', 'options', 'answer', 'level', 'category', 'status', 'update_time')

    form_columns = ('content', 'options', 'answer', 'level', 'category', 'status')

    can_view_details = True

    column_choices = {
        'level': LEVEL,
        'status':STATUS,
        'category': CATEGORY,
    }

    form_extra_fields = {
        'level': fields.SelectField(label='难度', choices=LEVEL, default=1),
        'status': fields.SelectField(label='状态', choices=STATUS, default=1),
        'category': fields.SelectField(label='分类', choices=CATEGORY, default=2),
    }

    column_filters = ('content', 'id_', 'options', 'level', 'category', 'status')

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.create_time = datetime.now()
            model.update_time = model.create_time
        else:
            model.update_time = datetime.now()
            return super(QuestionView, self).on_model_change(form, model, is_created)

    def after_model_change(self, form, model, is_created):
        redis.delete('question:{}'.format(model.id_))
        return super(QuestionView, self).after_model_change(form, model, is_created)


category = '百科知识'

question_view = QuestionView(Question, db.session, name='题目列表', category=category)
