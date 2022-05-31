# coding:utf-8
import json
import re
import wget

invalid_char = '"/\\|:<>*?'


def _get_dict_from_file(file_name):
    with open(file_name, encoding='utf-8') as fp:
        return json.load(fp=fp)


if __name__ == '__main__':
    dict_play = _get_dict_from_file('./json/6_.json')
    article_list = dict_play.get('events')
    for article in article_list:
        name = article.get('article').get('musics')[0].get('name')
        new_name = re.sub('["/\\|:<>*?]', ' ', name)
        url = article.get('article').get('musics')[0].get('url')
        wget.download(url, '%s.mp3' % new_name)
        print(name, url)


