# coding=utf-8

from snow.models.gsc import Gsc
import re
from snow.app import create_app
from snow.ext import db


def main():
    create_app().app_context().push()
    with open('query_result.csv', 'r') as f:
        objs = []
        for line in f.readlines():
            title, author, content = line.split(',')
            contents = re.split('[，。, ？? ！! ]', content.replace('"', ''))
            contents = [x for x in contents if x.strip()]
            ss = []
            for x in range(0, len(contents), 2):
                ss.append('，'.join(contents[x:x+2]) + '。\n')
            title, author, content = title.replace('"', ''), author.replace('"', ''), ''.join(ss)
            print(title)
            objs.append(Gsc(
                work_title=title,
                work_author=author,
                work_dynasty='唐',
                content=content,
                foreword='',
                intro='',
                annotation_='',
                translation='',
                master_comment='',
                baidu_wiki='',
                audio_id=0,
                layout='center',
                appreciation='',
            ))
            if len(objs) == 3000:
                db.session.bulk_save_objects(objs)
                db.session.commit()
                objs=[]
        if objs:
            db.session.bulk_save_objects(objs)
            db.session.commit()
