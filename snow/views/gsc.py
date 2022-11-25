# coding=utf-8
import flask_login as login
from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup
from wtforms import fields, validators

from snow.ext import db
from snow.models.gsc import Gsc
from snow.models.quotes import Quotes

DYNASTY = [
    ('宋', '宋'),
    ('唐', '唐'),
    ('元', '元'),
    ('现代', '现代'),
    ('五代十国', '五代十国'),
    ('上古', '上古'),
    ('商', '商'),
    ('周', '周'),
    ('秦', '秦'),
    ('汉', '汉'),
    ('三国', '三国'),
    ('晋', '晋'),
    ('南北朝', '南北朝'),
    ('隋', '隋'),
    ('金', '金'),
    ('明', '明'),
    ('清', '清'),
    ('民国', '民国'),
    ('近代', '近代'),
]


class GscAdmin(ModelView):
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

    can_view_details = True

    column_labels = {
        'id_': '编号',
        'work_title': '标题',
        'work_author': '作者',
        'work_dynasty': '朝代',
        'foreword': '前言',
        'content': '内容',
        'content_short': '内容',
        'translation': '翻译',
        'intro': '简介',
        'baidu_wiki': '百度wiki',
        'annotation_': '注释',
        'appreciation': '赏析',
        'master_comment': '辑评',
        'layout': '布局',
        'audio_id': '音频ID',
    }

    column_sortable_list = ('id_', )

    column_list = (
        'id_',
        'work_title',
        'work_author',
        'content_short',
        'audio_id',
    )
    column_filters = ('id_', 'work_title', 'work_author', 'work_dynasty', 'content', 'foreword')

    def _render_baidu_wiki(self, context, model, name):
        if model.baidu_wiki:
            return Markup('<a href="{}" target="_blank">{}</a>'.format(model.baidu_wiki, model.baidu_wiki))

    def _render_audio(self, context, model, name):
        if model.audio_id:
            return Markup(
                '<a href="https://songci.nos-eastchina1.126.net/audio/{}.m4a" '
                'target="_blank">https://songci.nos-eastchina1.126.net/audio/{}.m4a </a>'.format(
                    model.audio_id, model.audio_id
                )
            )

    def _render_translation(self, context, model, name):
        if model.translation:
            s = model.translation
            s = s.replace('\n', '<br>')
            return Markup(s)

    def _render_annotation(self, context, model, name):
        if model.annotation_:
            s = model.annotation_
            s = s.replace('\n', '<br>')
            return Markup('<div>' + s + '</div>')

    def _render_content(self, context, model, name):
        if model.content:
            s = model.content
            s = s.replace('\n', '<br>')
            return Markup('<div>' + s + '</div>')

    def _render_content_short(self, context, model, name):
        if model.content:
            return model.content[:28] + '...'

    def _render_foreward(self, context, model, name):
        if model.foreword:
            s = model.foreword
            s = s.replace('\n', '<br>')
            return Markup('<div>' + s + '</div>')

    def _render_master_comment(self, context, model, name):
        if model.master_comment:
            s = model.master_comment
            s = s.replace('\n', '<br>')
            return Markup('<div>' + s + '</div>')

    def _render_appreciation(self, context, model, name):
        if model.appreciation:
            s = model.appreciation
            s = s.replace('\n', '<br>')
            return Markup('<div>' + s + '</div>')

    def _render_intro(self, context, model, name):
        if model.intro:
            s = model.intro
            s = s.replace('\n', '<br>')
            return Markup('<div>' + s + '</div>')

    column_formatters = {
        'baidu_wiki': _render_baidu_wiki,
        'audio_id': _render_audio,
        'translation': _render_translation,
        'annotation_': _render_annotation,
        'content': _render_content,
        'content_short': _render_content_short,
        'foreward': _render_foreward,
        'master_comment': _render_master_comment,
        'appreciation': _render_appreciation,
        'intro': _render_intro,
        'layout': lambda a, b, c, d: '居中' if c.layout == 'center' else '缩进',
        'work_author': lambda a, b, c, d: Markup(
            '<a  target="_blank" href="https://baike.baidu.com/item/{}">{}</a>'.format(c.work_author, c.work_author)
        )
    }

    form_extra_fields = {
        'content': fields.TextAreaField(label='内容', default='', validators=[validators.DataRequired()]),
        'foreword': fields.TextAreaField(label='前言', default=''),
        'translation': fields.TextAreaField(label='翻译', default=''),
        'intro': fields.TextAreaField(label='简介', default=''),
        'annotation_': fields.TextAreaField(label='注释', default=''),
        'appreciation': fields.TextAreaField(label='赏析', default=''),
        'master_comment': fields.TextAreaField(label='辑评', default=''),
        'audio_id': fields.IntegerField(label='音频id', default=0),
        'layout': fields.SelectField(label='布局', choices=[('indent', '缩进'), ('center', '居中')]),
        'work_dynasty': fields.SelectField(label='朝代', validate_choice=True, choices=DYNASTY),
    }

    form_columns = (
        'work_title', 'work_dynasty', 'work_author', 'foreword', 'content', 'translation', 'intro', 'annotation_',
        'appreciation', 'master_comment', 'layout', 'baidu_wiki', 'audio_id'
    )

    def on_model_change(self, form, model, is_created=True):
        if is_created:
            with db.session.no_autoflush:
                gsc = Gsc.query.order_by(Gsc.id_.desc()).first()
                if gsc:
                    model.id_ = gsc.id_ + 1
                else:
                    model.id_ = 1
        if form.data['content']:
            model.content = form.data['content'].replace('　', '')
            model.content = model.content.replace('\n\r\n', '\n')
        if form.data['foreword']:
            model.foreword = form.data['foreword'].replace('　', '')
            model.foreword = model.foreword.replace('\n\r\n', '\n')
        if form.data['translation']:
            model.translation = form.data['translation'].replace('　', '')
            model.translation = model.translation.replace('\n\r\n', '\n')
        if form.data['intro']:
            model.intro = form.data['intro'].replace('　', '')
            model.intro = model.intro.replace('\n\r\n', '\n')
        if form.data['annotation_']:
            model.annotation_ = form.data['annotation_'].replace('　', '')
            model.annotation_ = model.annotation_.replace('\n\r\n', '\n')
        if form.data['appreciation']:
            model.appreciation = form.data['appreciation'].replace('　', '')
            model.appreciation = model.appreciation.replace('\n\r\n', '\n')
        if form.data['master_comment']:
            model.master_comment = form.data['master_comment'].replace('　', '')
            model.master_comment = model.master_comment.replace('\n\r\n', '\n')
        return super(GscAdmin, self).on_model_change(form, model, is_created)


class QuotesView(ModelView):

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
        'id_': '编号',
        'quote': '名句',
        'author': '作者',
    }

    form_columns = ('quote', 'author')

    column_sortable_list = ()

    column_filters = ('quote', 'author')

    column_default_sort = ('id_', True)

    column_formatters = {
        'quote': lambda a, b, c, d: Markup(
            '<a href="https://www.baidu.com/s?wd={}" \
            target="_blank" style="text-decoration: none;color: #003472;">{}</a>'.format(c.quote, c.quote)
        ),
    }

    can_view_details = True


category = 'i古诗词'

gsc_view = GscAdmin(Gsc, db.session, name='诗词列表', category=category)
quotes_view = QuotesView(Quotes, db.session, name='诗词名句', category=category)
