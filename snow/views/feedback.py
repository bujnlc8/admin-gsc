# coding=utf-8
import logging
import os

import flask_login as login
import requests
from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup
from wtforms import ValidationError

from snow.ext import db, redis
from snow.models.feedback import Feedback


class FeedbackView(ModelView):
    page_size = 12

    def is_accessible(self):
        return login.current_user.is_authenticated and (login.current_user.role & 8)

    @property
    def can_create(self):
        return False

    @property
    def can_edit(self):
        return self.is_accessible() and (login.current_user.role & 32)

    @property
    def can_delete(self):
        return self.is_accessible() and (login.current_user.role & 64)

    column_sortable_list = ('id_',)

    column_labels = {
        'id_': 'ID',
        'uid': '用户id',
        'nickname': '昵称',
        'question_id': '问题ID',
        'type_': '类型',
        'status': '状态',
        'create_time': '创建时间',
        'remark': '备注',
    }

    column_list = ('id_', 'uid', 'nickname', 'question_id', 'type_', 'status', 'remark', 'create_time')

    can_view_details = True

    column_choices = {
        'status': [(0, '待审核'), (1, '审核通过')],
    }
    column_editable_list = ('status',)

    def _render_question(self, context, model, name):
        return Markup(
            '<a href="{}">{}</>'.format('/question/details/?id={}'.format(model.question_id), model.question_id)
        )

    def _rendertype_(self, context, model, name):
        s = []
        # 1题干错误 2 选项错误 4 答案错误 8 其他
        if model.type_ & 1:
            s.append('题干错误')
        if model.type_ & 2:
            s.append('选项错误')
        if model.type_ & 4:
            s.append('答案错误')
        if model.type_ & 8:
            s.append('其他')
        if model.type_ & 16:
            s.append('分类错误')
        return '、'.join(s)

    column_formatters = {
        'question_id': _render_question,
        'type_': _rendertype_,
    }

    column_filters = ('id_', 'uid', 'nickname', 'type_', 'status')

    column_default_sort = ('id_', True)

    def update_model(self, form, model):
        if model.status == 1:
            raise ValidationError('不能再修改')
        if 'status' in form.data and form.data['status'] == 1:
            url = os.environ.get('SNOW_COIN_URL')
            key = redis.get('challenge:{}:token'.format(model.uid))
            headers = {
                'Authorization': 'Bearer {}_{}'.format(
                    model.uid,
                    key.decode('utf-8').replace('"', ''),
                )
            }
            res = requests.post(
                url,
                data={'source': 8},
                headers=headers,
            )
            if res.status_code != 200:
                raise ValidationError('赠送百科币失败')
        return super(FeedbackView, self).update_model(form, model)


category = '百科知识'

feedback_view = FeedbackView(Feedback, db.session, name='用户反馈', category=category)
