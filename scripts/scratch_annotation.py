# coding=utf-8

import hashlib
import json
import re

import requests
from bs4 import BeautifulSoup

from snow.app import create_app
from snow.ext import db
from snow.models.gsc import Gsc


def get_item():
    limit = 5000
    offset = 40194
    while True:
        records = Gsc.query.offset(offset).limit(limit).all()
        for x in records:
            yield x
        if len(records) < limit:
            break
        offset += limit


SearchUrl = 'https://so.gushiwen.cn/search.aspx?value=%s%s'
DetailUrl = 'https://so.gushiwen.cn/shiwenv_%s.aspx'
AnnoUrl = 'https://so.gushiwen.cn/nocdn/ajaxfanyi.aspx?id=%s'

f = open('a.json', 'w')

res = {}

def main():
    create_app().app_context().push()
    for x in get_item():
        try:
            if x.annotation_:
                continue
            r = get(x.work_title, x.work_author, x.content[:108])
            if r:
                x.annotation_ = r
                try:
                    db.session.add(x)
                    db.session.commit()
                except:
                    db.session.rollback()
                    db.session.add(x)
                    db.session.commit()
                print(x.work_title, x.work_author)
        except Exception as e:
            print(x, e)

headers = {
    'cookie': 'ASP.NET_SessionId=dc2wrcjil00mkwvswbnwbkaf; codeyzgswso=85efdb305fa6583c;gsw2017user=2272208%7c6A5471B38CFFFF27880E4F7E9679CF7A; login=flase; wxopenid=ouY_U1YPb2WfkAWqqT5sGgOHSfkU;'
}


def get(title, author, content):
    resp = requests.get(SearchUrl % (title, author), headers=headers)
    if resp.status_code != 200:
        print(title, author, 'status_code: ', resp.status_code)
        return
    h = hashlib.md5(content.replace('，', '').replace('、', '').replace('：', '').replace('“', '').
                        replace('！', '').replace('。', '').replace('？', '').replace('”', '').replace('\n', '').encode('utf-8')[:12]).hexdigest()
    s = BeautifulSoup(resp.text, 'html.parser')
    s = s.find_all('div', class_="contson")
    for x in s:
        content = x.contents
        content = ''.join(map(lambda x: str(x), content)).replace('\n', '').replace('<p>', '').replace('</p>', '')
        h1 = hashlib.md5(content.replace('，', '').replace('、', '').replace('：', '').replace('“', '').replace('！', '').replace('。', '').replace('？', '').replace('”', '').replace('\n', '').encode('utf-8')[:12]).hexdigest()
        if h == h1:
            id_ = x.attrs['id'][7:]
            detail_url = DetailUrl % id_
            print(detail_url)
            text = requests.get(detail_url, headers=headers).text
            ss = BeautifulSoup(text, 'html.parser')
            sss = ss.find_all(href=re.compile('javascript:fanyiShow'))
            if not sss:
                anno_s = BeautifulSoup(text, 'html.parser')
            else:
                h = sss[0].attrs['href']
                anno_id = re.search('\'.*\'', h).group().replace("'", '')
                if not anno_id:
                    print('找不到id', title, author)
                    return
                req = requests.get(AnnoUrl % anno_id, headers=headers).text.replace(' ', '')
                anno_s = BeautifulSoup(req, 'html.parser')
            anno_s_ = anno_s.find_all(text='注释')
            if not anno_s_:
                anno_s = anno_s.find_all(text='注解')
                if not anno_s:
                    print('未找到注释', title, author)
                    return
            else:
                anno_s = anno_s_
            anno_s = anno_s[0].parent.parent
            for i in range(100):
                try:
                    a = anno_s.a
                    a.replace_with(a.text)
                except:
                    break
            anno_s = str(anno_s).replace('</p>', '').replace('</div>', '').replace('▲', '').split('<br/>')[1:]
            anno_s = '$$'.join(map(lambda x: x.replace('\n', ''), anno_s)).replace('\n', '').replace('$$', '\n').replace('\r', '').replace('\t', '')
            anno_s = anno_s.replace('</strong>', '')
            anno_s = anno_s.replace('<strong>', '')
            return anno_s
