import os
import requests
import pprint
import jmespath
import time
from furl import furl

this_dir = os.path.dirname(os.path.abspath(__file__))


def __directory_exist_check(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


video_path = os.path.join(this_dir, time.strftime("%Y-%m-%d"))
__directory_exist_check(video_path)


def get_hot_list():
    url = 'https://api3-normal-c-hl.amemv.com/aweme/v1/hot/search/list/?detail_list=1&mac_address=A0%3A86%3AC6%3AA8%3ADB%3A5D&source=0&current_word&words_in_panel=+&trend_entry_word&os_api=23&device_type=MI%204LTE&ssmix=a&manifest_version_code=110502&dpi=480&uuid=865931028491629&app_name=aweme&version_name=11.5.1&ts=1593505161&cpu_support64=false&app_type=normal&ac=wifi&host_abi=armeabi-v7a&update_version_code=11519900&channel=xiaomi&_rticket=1593505161669&device_platform=android&iid=1363049466040444&version_code=110501&mac_address=A0%3A86%3AC6%3AA8%3ADB%3A5D&cdid=5d857c06-4ded-46c0-9380-ccd777da3256&openudid=db5e62a9bcba313f&device_id=34634747427&resolution=1080*1920&os_version=6.0.1&language=zh&device_brand=Xiaomi&aid=1128'
    res = requests.get(url)
    item = res.json()
    # pprint.pprint(item)
    dlist = jmespath.search('data.word_list', item)
    return dlist


def get_word_detail(word):
    url = 'https://api3-normal-c-hl.amemv.com/aweme/v1/hot/search/video/list/?offset=0&count=50&source=trending_page&is_ad=0&item_id_list&is_trending=0&city_code&related_gids&os_api=23&device_type=MI%204LTE&ssmix=a&manifest_version_code=110502&dpi=480&uuid=865931028491629&app_name=aweme&version_name=11.5.1&ts=1593505798&cpu_support64=false&app_type=normal&ac=wifi&host_abi=armeabi-v7a&update_version_code=11519900&channel=xiaomi&_rticket=1593505800138&device_platform=android&iid=1363049466040444&version_code=110501&mac_address=A0%3A86%3AC6%3AA8%3ADB%3A5D&cdid=5d857c06-4ded-46c0-9380-ccd777da3256&openudid=db5e62a9bcba313f&device_id=34634747427&resolution=1080*1920&os_version=6.0.1&language=zh&device_brand=Xiaomi&aid=1128'
    url += '&hotword=' + word
    data = requests.get(url)
    data = data.json()
    res = []
    for item in data['aweme_list']:
        tmp = {}
        tmp['video_url'] = jmespath.search('video.play_addr.url_list[0]', item)
        tmp['word'] = word
        tmp['desc'] = jmespath.search('desc', item)
        tmp['author'] = jmespath.search('author.nickname', item)
        ctime = jmespath.search('create_time', item)
        try:
            ctime = time.localtime(ctime)
            tmp['create_time'] = time.strftime("%Y-%m-%d %H:%M:%S", ctime)
        except Exception as e:
            pass

        res.append(tmp)
    # pprint.pprint(res)
    return res


def save_data(dlist, item):
    for tmp in dlist:
        name = str(int(time.time() * 1000))
        title = tmp['word']
        title_path = os.path.join(video_path, title)
        __directory_exist_check(title_path)
        print('save--', title)
        tmp.update({'video_count': item.get('video_count', ''), 'hot_value': item.get('hot_value', '')})
        try:
            # save_text(tmp, name)
            save_path = os.path.join(title_path, '{}.mp4'.format(name))
            save_video(tmp['video_url'], save_path)
        except Exception as e:
            print('save error:', e)


def save_text(item, name):
    with open(os.path.join(this_dir, 'data', name + '.txt'), 'w', encoding='utf-8') as f:
        for key, value in item.items():
            f.write(key + '\t' + str(value) + '\n')


def save_video(url, save_path):
    res = requests.get(url)
    content = res.content
    f = furl(url)
    mime_type = f.args['mime_type']
    if mime_type:
        suffix = mime_type.split('_')[-1]
        with open(save_path, 'wb') as f:
            f.write(content)


if __name__ == '__main__':
    hot_list = get_hot_list()
    print(hot_list)
    for item in hot_list[1:]:
        try:
            dlist = get_word_detail(item['word'])
            save_data(dlist, item)
        except TypeError as e:
            continue


