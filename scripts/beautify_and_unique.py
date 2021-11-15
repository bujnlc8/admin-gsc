# coding=utf-8


import hashlib

from snow.app import create_app
from snow.ext import db
from snow.models.gsc import Gsc


def get_item():
    limit = 5000
    offset = 0
    while True:
        records = Gsc.query.offset(offset).limit(limit).all()
        for x in records:
            yield x
        if len(records) < limit:
            break
        offset += limit


def main():
    create_app().app_context().push()
    for x in get_item():
        try:
            if x.foreword:
                x.foreword = x.foreword.replace('\r\n', '\n')
            else:
                x.foreword = ''
            if x.content:
                x.content = x.content.replace('\r\n', '\n')
            else:
                x.content = ''
            if x.appreciation:
                x.appreciation = x.appreciation.replace('\r\n', '\n')
            else:
                x.appreciation = ''
            if x.translation:
                x.translation = x.translation.replace('\r\n', '\n')
            else:
                x.translation = ''
            if x.intro:
                x.intro = x.intro.replace('\r\n', '\n')
            else:
                x.intro = ''
            if x.annotation_:
                x.annotation_ = x.annotation_.replace('\r\n', '\n')
            else:
                x.annotation_ = ''
            if x.master_comment:
                x.master_comment = x.master_comment.replace('\r\n', '\n')
            else:
                x.master_comment = ''
            db.session.add(x)
            db.session.commit()
            print(x.work_title)
        except Exception as e:
            print(e)


exist = {}


def remove_exist():
    r = []
    create_app().app_context().push()
    for x in get_item():
        h = hashlib.md5(x.content.replace('，', '').replace('、', '').replace('：', '').replace('“', '').
                        replace('！', '').replace('。', '').replace('？', '').replace('”', '').replace('\n', '').encode('utf-8')[:48]).hexdigest()
        if h in exist:
            print(x.id_, x.work_title)
            r.append(x.id_)
        else:
            exist[h] = 1
    print(r)
