import requests
from urllib.parse import urlencode
from requests import codes
import os
from hashlib import md5
from multiprocessing.pool import Pool
import re
import json
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
}


def get_page_index(offset, keyword):
    params = {
        'aid': '24',
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1',
        'from': 'search_tab',
        'pd': 'synthesis'
    }
    base_url = 'https://www.toutiao.com/api/search/content/'
    try:
        response = requests.get(base_url, params=params, headers=headers)
        print(response.url)
        if 200 == response.status_code:
            print(response.json())
            return response.json()

        return None
    except requests.ConnectionError:
        return None


def parse_page_index(data):
    if data and 'data' in data.keys():
        for item in data.get('data'):
            if item.get('article_url'):
                yield item.get('article_url')


def get_page_detail(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except requests.ConnectionError:
        return None


def parse_page_detail(html):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    images_pattern = re.compile('gallery:\sJSON.parse\((.*?)\),', re.S)
    result = re.search(images_pattern, html)
    if result:
        try:
            data = json.loads(json.loads(result.group(1)))
            if data and 'sub_images' in data.keys():
                sub_images = data.get('sub_images')
                images = [item['url'] for item in sub_images]
                return {
                    'title': title,
                    'images': images
                }
        except JSONDecodeError:
            print('Json error')


print('succ')


def save_image(item):
    img_path = 'img' + os.path.sep + item.get('title')
    print('succ2')
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    try:
        for image in item.get('images'):
            response = requests.get(image, headers=headers)
            if codes.ok == response.status_code:
                file_path = img_path + os.path.sep + '{file_name}.{file_suffix}'.format(
                    file_name=md5(response.content).hexdigest(),
                    file_suffix='jpg')
                if not os.path.exists(file_path):
                    print('succ3')
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    print('Downloaded image path is %s' % file_path)
                    print('succ4')
                else:
                    print('Already Downloaded', file_path)
    except requests.ConnectionError:
        print('Failed to Save Image，item %s' % item)


def main(offset, keyword='街拍'):
    html = get_page_index(offset, keyword)
    for url in parse_page_index(html):
        print(url)
        html = get_page_detail(url)
        if html:
            item = parse_page_detail(html)
            if item:
                save_image(item)


GROUP_START = 0
GROUP_END = 7

if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START, GROUP_END + 1)])
    pool.map(main, groups)
    pool.close()
    pool.join()
