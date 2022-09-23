# coding=utf-8

from snow.ext import db
from snow.models.gsc import Gsc
from snow.app import create_app
import re
import time
import os


import requests

cookies = {
    '_xmLog': 'h5&e3fa0829-cc4c-43e3-8a6a-19b2a103b6fe&2.4.7-alpha.3',
    'xm-page-viewid': 'ximalaya-web',
    'x_xmly_traffic': 'utm_source%253A%2526utm_medium%253A%2526utm_campaign%253A%2526utm_content%253A%2526utm_term%253A%2526utm_from%253A',
    'Hm_lvt_4a7d8ec50cfd6af753c4f8aee3425070': '1637490424,1637490429,1637490461,1637490471',
    'Hm_lpvt_4a7d8ec50cfd6af753c4f8aee3425070': '1637678842',
}

headers = {
    'Connection': 'keep-alive',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    'DNT': '1',
    'xm-sign': 'de49e8a38c39663d91c87c7b2f59fee6(62)1637680304447(0)1637680181932',
    'sec-ch-ua-mobile': '?0',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36',
    'sec-ch-ua-platform': '"macOS"',
    'Accept': '*/*',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.ximalaya.com/gerenchengzhang/221789/p2/',
    'Accept-Language': 'zh,en-US;q=0.9,en;q=0.8',
}


re_words = re.compile('[\u4e00-\u9fa5]+')


def get_author_title(title):
    title = re.findall(re_words, title)
    print(title)
    if len(title) >= 2:
        return title[0] , title[1]


def get(album_id):
    create_app().app_context().push()
    for x in range(1, 100):
        params = (
            ('albumId', '{}'.format(album_id)),
            ('pageNum', '{}'.format(x)),
        )
        response = requests.get('https://www.ximalaya.com/revision/album/v1/getTracksList',
                                headers=headers, params=params, cookies=cookies)
        if response.status_code != 200:
            print(album_id, x, 'status_code', response.status_code)
            continue
        response = response.json()
        tracks = response['data']['tracks']
        if not tracks:
            continue
        for track in tracks:
            title = track['title']
            title = get_author_title(title)
            if not title:
                continue
            work_title, work_author = title
            gsc = Gsc.query.filter(Gsc.work_title.like(
                '%' + work_title + '%'), Gsc.work_author == work_author).first()
            if not gsc:
                print(work_title, work_author, '找不到记录')
                continue
            if gsc.audio_id > 0:
                continue
            track_id = track['trackId']
            print(gsc)
            params = (
                ('id', '{}'.format(track_id)),
                ('ptype', '1'),
            )
            try_times = 30
            while try_times > 0:
                try:
                    response = requests.get(
                        'https://www.ximalaya.com/revision/play/v1/audio', headers=headers, params=params, cookies=cookies)
                    response = response.json()
                    src = response['data']['src']
                    if not src:
                        break
                    if os.path.exists('audio/{}.m4a'.format(gsc.id_)):
                        break
                    with open('audio/{}.m4a'.format(gsc.id_), 'wb') as f:
                        f.write(requests.get(src).content)
                except:
                    try_times -= 1
                    time.sleep(2)
                else:
                    break
