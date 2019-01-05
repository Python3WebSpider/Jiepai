import requests
from urllib.parse import urlencode
from requests import codes
import os
from hashlib import md5
from multiprocessing.pool import Pool


def get_page(offset):
    params = {
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1',
        'from': 'search_tab'
    }
    base_url = 'https://www.toutiao.com/search_content/?'
    url = base_url + urlencode(params)
    try:
        resp = requests.get(url)
        if codes.ok == resp.status_code:
            return resp.json()
    except requests.ConnectionError:
        return None


def get_images(json):
    if json.get('data'):
        data = json.get('data')
        for item in data:
            if item.get("title") is None:
                continue
            if item.get('image_list') is not  None:
                title = item.get('title')
                if "||" in title:
                    title = title.replace("||", " ")
                images = item.get('image_list')
                for image in images:
                    url = image.get("url")
                    largeUrl = url.replace("list","large")
                    # 生成器
                    yield {
                        'image': 'http:' + largeUrl,
                        'title': title
                    }

def save_image(item):
    img_path = 'img' + os.path.sep + item.get('title')
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    try:
        resp = requests.get(item.get('image'))
        if codes.ok == resp.status_code:
            file_path = img_path + os.path.sep + '{file_name}.{file_suffix}'.format(
                file_name=md5(resp.content).hexdigest(),
                file_suffix='jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(resp.content)
                print('Downloaded image,save_path is %s' % file_path)
            else:
                print('Already Downloaded', file_path)
    except requests.ConnectionError:
        print('Failed to Save Image，item %s' % item)


def main(offset):
    json = get_page(offset)
    for item in get_images(json):
        print(item)
        save_image(item)


if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(0, 8)])
    pool.map(main, groups)
    pool.close()
    pool.join()
