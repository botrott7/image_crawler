import re
import os

import requests

from dotenv import load_dotenv
from logs.logis import logger
from bs4 import BeautifulSoup as BS4
import urllib.parse

load_dotenv()

URL = os.getenv('URL')
CLASS_PATTERN = re.compile(r'[A-Za-z0-9_]{16}')


def get_page(phrase, page):
    link = URL + phrase
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36'
    }
    params = {'page': page, 'phrase': phrase, 'sort': 'mostpopular'}
    request = requests.get(link, headers=headers, params=params)
    return request.text


def is_404(html):
    page = BS4(html, 'html.parser')

    imgs = page.find_all('img')  # Поиск всех тегов img на странице

    # Проверка наличия изображений с классами, удовлетворяющими регулярному выражению
    for img in imgs:
        img_class = img.get('class')
        if img_class and CLASS_PATTERN.match(' '.join(img_class)):
            return False  # Найдены изображения

    return True  # Изображения не найдены


def get_imgs_from_page(phrase, page):
    html = get_page(phrase, page)
    images = []

    if is_404(html):
        return []

    img_node = BS4(html, 'html.parser')

    for img in img_node.select('img[class]'):
        img_class = img.get('class')
        if img_class and CLASS_PATTERN.match(' '.join(img_class)):
            img_src = img.get('src')
            if img_src:
                logger.info(f'Получена ссылка на фото: {img_src}')
                images.append(img_src)

    return images


def get_images(query, pages):
    query = urllib.parse.quote(query)
    images = []
    for i in range(pages):
        num_of_page = i + 1
        img = get_imgs_from_page(query, num_of_page)

        if not img:
            break
        else:
            images += img
    return images


def save_image(folder, link):
    image = requests.get(link, stream=True)
    filename = link.split('/')[-1].split('?')[0]  # Получаем имя файла из URL
    filename = urllib.parse.unquote(filename)  # Декодируем URL-кодированные символы в имени файла
    full_path = os.path.join(folder, filename)  # Формируем полный путь к сохранению файла

    with open(full_path, 'wb') as file:
        for chunk in image.iter_content(chunk_size=1024):
            file.write(chunk)
    logger.info(f'Файл сохранен: {full_path}')


def download_images(folder, phrase, page):
    images = get_images(phrase, page)
    for image in images:
        try:
            save_image(folder, image)
        except Exception as error:
            logger.error(f'Проблема с записью файла download_images: {error}')
