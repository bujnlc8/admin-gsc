# coding=utf-8

import requests
from snow.ext import db
from snow.models.gsc import Gsc
from snow.app import create_app

headers = {
    'authority': 'avoscloud.com',
    'x-lc-ua': 'LeanCloud-JS-SDK/3.15.0 (Browser)',
    'dnt': '1',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'content-type': 'application/json;charset=UTF-8',
    'x-lc-sign': 'f7b2d3ee3f3598a4e28536b28f586384,1636278803243',
    'x-lc-id': '9pq709je4y36ubi10xphdpovula77enqrz27idozgry7x644',
    'x-lc-prod': '1',
    'sec-ch-ua-platform': '"macOS"',
    'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    'accept': '*/*',
    'origin': 'http://lib.xcz.im',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'http://lib.xcz.im/',
    'accept-language': 'zh,en-US;q=0.9,en;q=0.8',
}


def _sync(page, author):
    create_app().app_context().push()
    data = '{"page":' + str(page) + \
        ',"perPage":200, "authorId": "' + author + '"}'
    response = requests.post(
        'https://avoscloud.com/1.1/call/getWorksByAuthor', headers=headers, data=data)
    if response.status_code != 200:
        print(page, 'error')
        return -1
    resp = response.json()
    objs = []
    for x in resp['result']:
        try:
            exist = Gsc.query.filter(
                Gsc.work_title == x['title'], Gsc.work_author == x['authorName']).first()
            if exist:
                continue
            if x['annotation']:
                annotation = x['annotation'].replace('\r\n', '\n')
            else:
                annotation = ''
            if x['appreciation']:
                appreciation = x['appreciation'].replace('\r\n', '\n')
            else:
                appreciation = ''
            dynasty = x['dynasty']
            author = x['authorName']
            baidu_wiki = x['baiduWiki']
            if x['content']:
                content = x['content'].replace('\r\n', '\n')
            else:
                content = ''
            if x['foreword']:
                foreword = x['foreword'].replace('\r\n', '\n')
            else:
                foreword = ''
            if x['intro']:
                intro = x['intro'].replace('\r\n', '\n')
            else:
                intro = ''
            if x['layout']:
                layout = x['layout'].replace('\r\n', '\n')
            else:
                layout = 'indent'
            if x['translation']:
                translation = x['translation'].replace('\r\n', '\n')
            else:
                translation = ''
            if x['masterComment']:
                master_comment = x['masterComment'].replace('\r\n', '\n')
            else:
                master_comment = ''
            obj = Gsc(
                work_title=x['title'],
                work_author=author,
                work_dynasty=dynasty,
                content=content,
                foreword=foreword,
                intro=intro,
                annotation_=annotation,
                translation=translation,
                master_comment=master_comment,
                baidu_wiki=baidu_wiki,
                audio_id=0,
                layout=layout,
                appreciation=appreciation,
            )
            objs.append(obj)
        except Exception as e:
            print(e)
            print(x['objectId'])
    if objs:
        db.session.bulk_save_objects(objs)
        db.session.commit()
    return len(resp['result']y


def sync(author_id):
    for x in range(1, 200):
        if _sync(x, author_id) == 0:
            break
