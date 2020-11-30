import os
import random
import requests
import urllib3
from dotenv import load_dotenv
from pathlib import Path
from utils import download_image


COMICS_URL = 'https://xkcd.com{}info.0.json'
VK_URL_METHOD = 'https://api.vk.com/method'


def get_random_xkcd_comics():
    # define the total number of comics
    response = requests.get(COMICS_URL.format('/'))
    response.raise_for_status()
    comics = response.json()
    if 'num' in comics:
        # get a random comics
        total_comics = comics['num']
        number_comics = random.randint(1, total_comics)
        response = requests.get(COMICS_URL.format(f'/{number_comics}/'))
        response.raise_for_status()
        comics = response.json()
        comics_image_url = comics['img']
        comics_image_name = comics['img'].split('/')[-1]
        comics_title = comics['alt']
        download_image(comics_image_url, comics_image_name)
        return {'title': comics_title, 'image': comics_image_name}


def main():
    load_dotenv()
    VK_ACCESS_TOKEN = os.getenv('VK_ACCESS_TOKEN')
    VK_GROUP_ID = os.getenv('VK_GROUP_ID')
    params = {'group_id': VK_GROUP_ID,
              'access_token': VK_ACCESS_TOKEN, 'v': '5.126'}
    urllib3.disable_warnings()

    comics = get_random_xkcd_comics()

    # get link to upload server
    response = requests.get(
        f'{VK_URL_METHOD}/photos.getWallUploadServer', params=params)
    response.raise_for_status()
    wall_upload_server = response.json()['response']
    if 'error' in wall_upload_server:
        print(wall_upload_server['error']['error_msg'])
        return

    # upload comics image into server
    with open(comics['image'], 'rb') as file:
        url = wall_upload_server['upload_url']
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
        upload_photo = response.json()
        if not upload_photo['photo']:
            return

    # save comics image in albom
    params['photo'] = upload_photo['photo']
    params['server'] = upload_photo['server']
    params['hash'] = upload_photo['hash']
    response = requests.post(
        f'{VK_URL_METHOD}/photos.saveWallPhoto', params=params)
    response.raise_for_status()
    wall_photo = response.json()['response'][0]
    if 'error' in wall_photo:
        print(wall_photo['error']['error_msg'])
        return

    # publish comics on group
    params['owner_id'] = -(int(VK_GROUP_ID))
    params['from_group'] = 1
    params['attachments'] = f'photo{wall_photo["owner_id"]}_{wall_photo["id"]}'
    params['message'] = comics['title']
    response = requests.post(
        f'{VK_URL_METHOD}/wall.post', params=params)
    response.raise_for_status()
    uploaded_wall_post = response.json()['response']
    if 'error' in uploaded_wall_post:
        print(uploaded_wall_post['error']['error_msg'])
        return

    Path(comics['image']).unlink()


if __name__ == '__main__':
    main()