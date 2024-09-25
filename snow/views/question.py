# coding=utf-8
import os
from datetime import datetime

import flask_login as login
import requests
from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup
from wtforms import fields

from snow.ext import db, redis
from snow.models.question import Question
from snow.models.region import Region


def get_category():
    try:
        url = os.environ.get('SNOW_COIN_URL', '').replace('coin/operate', 'common/category')
        data = requests.get(url).json()['data']
        res = []
        for k, v in enumerate(data[1:]):
            res.append((k + 1, v))
        return res
    except Exception:
        return


CATEGORY = get_category() or [
    (1, '财经'),
    (2, '百科'),
    (3, '历史'),
    (4, '地理'),
    (5, '诗词'),
    (6, '驾考科目一'),
    (7, '驾考科三理论'),
    (8, '交通规则'),
]

LEVEL = [(1, '简单'), (2, '中等'), (3, '困难')]

STATUS = [(1, '正常'), (0, '删除')]

SERIAL = ['A', 'B', 'C', 'D']


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

    column_sortable_list = ('id_',)

    column_labels = {
        'id_': 'ID',
        'content': '题目',
        'options': '选项',
        'answer': '答案',
        'level': '难度',
        'category': '分类',
        'status': '状态',
        'analysis': '答案解析',
        'create_time': '创建时间',
        'update_time': '更新时间',
    }

    column_list = (
        'id_',
        'content',
        'options',
        'answer',
        'level',
        'category',
        'status',
        'update_time',
    )

    form_columns = (
        'content',
        'options',
        'answer',
        'level',
        'category',
        'analysis',
        'status',
    )
    can_view_details = True

    column_choices = {
        'level': LEVEL,
        'status': STATUS,
        'category': CATEGORY,
    }

    def _render_content(self, context, model, name):
        if '###' in model.content:
            content, image = model.content.split('###')
            if '.mp4' in image:
                return Markup(
                    '<span>{}</span><br><video width="300" src="{}" autoplay="autoplay" controls="controls" loop="loop"></video>'.format(
                        content, image
                    )
                )
            return Markup('<span>{}</span><br><image src="{}" style="width:200px;"/>'.format(content, image))
        return Markup('<div>{}<div>'.format(model.content.replace('\n', '<br/>')))

    def _render_options(self, context, model, name):
        options = model.options.split('|')
        s = ''
        if 'https://' in model.options:
            for x in enumerate(options):
                s += '{}、<image src="{}" style="width:180px;"/><br><br>'.format(SERIAL[x[0]], x[1])
            return Markup(s)
        for x, y in enumerate(options):
            s += SERIAL[x] + '、' + y + '<br>'
        return Markup(s)

    column_formatters = {
        'content': _render_content,
        'options': _render_options,
        'answer': lambda a, b, c, d: SERIAL[c.answer - 1],
        'analysis': lambda a, b, c, d: Markup('<div>{}</div>'.format(c.analysis.replace('\n', '<br/>')))
        if c.analysis
        else '无',
    }

    form_extra_fields = {
        'options': fields.StringField(label='选项', default='', description='多个选项以`|`隔开'),
        'level': fields.SelectField(label='难度', choices=LEVEL, default=1),
        'status': fields.SelectField(label='状态', choices=STATUS, default=1),
        'category': fields.SelectField(label='分类', choices=CATEGORY, default=2),
        'analysis': fields.TextAreaField(
            label='答案解析',
            default='',
            description='支持有限的html标签，比如`img`, 具体见`https://developers.weixin.qq.com/miniprogram/dev/component/rich-text.html`',
        ),
    }

    column_filters = ('content', 'id_', 'options', 'level', 'category', 'status')

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.create_time = datetime.now()
            model.update_time = model.create_time
        else:
            model.update_time = datetime.now()
        model.content = form.data['content'].strip().replace(' ', '')
        model.options = form.data['options'].strip().replace(' ', '').replace('｜', '|')
        return super(QuestionView, self).on_model_change(form, model, is_created)

    def after_model_change(self, form, model, is_created):
        redis.delete('question:{}'.format(model.id_))
        return super(QuestionView, self).after_model_change(form, model, is_created)


class RegionView(ModelView):
    page_size = 12

    def is_accessible(self):
        return login.current_user.is_authenticated

    @property
    def can_create(self):
        return self.is_accessible() and (login.current_user.role & 1)

    @property
    def can_edit(self):
        return self.is_accessible() and (login.current_user.role & 2)

    @property
    def can_delete(self):
        return self.is_accessible() and (login.current_user.role & 4)

    column_labels = {
        'region_code': '代码',
        'name': '名称',
        'discard_year': '废弃年份',
    }

    def render_name(self, context, model, name) -> str:
        parent_region_codes = [f'{model.region_code[:2]}0000', f'{model.region_code[:4]}00']
        regions = Region.get_by_region_codes(parent_region_codes)
        names = [x.name for x in regions]
        names.append(model.name)
        return ''.join(names)

    column_formatters = {
        'name': render_name,
    }

    column_list = ('region_code', 'name', 'discard_year')

    form_columns = ('region_code', 'name', 'discard_year')

    column_sortable_list = ()

    column_filters = ('region_code', 'name', 'discard_year')

    column_default_sort = ('region_code', False)

    can_view_details = True

    column_details_list = ('region_code', 'name', 'discard_year')


category = '百科知识'

question_view = QuestionView(Question, db.session, name='题目列表', category=category)
region_view = RegionView(Region, db.session, name='行政区划', category=category)
