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
    """ download random comics from xkcd.com """
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
        (_, comics_image_name) = os.path.split(comics['img'])
        comics_title = comics['alt']
        download_image(comics_image_url, comics_image_name)
        return {'title': comics_title, 'image': comics_image_name}


def get_upload_server(params):
    """ get link to upload server """
    response = requests.get(
        f'{VK_URL_METHOD}/photos.getWallUploadServer', params=params)
    response.raise_for_status()
    wall_upload_server = response.json()['response']
    if 'error' in wall_upload_server:
        raise Exception(wall_upload_server['error']['error_msg'])
    return wall_upload_server


def upload_image(image, upload_server_url):
    """ upload comics image into server """
    with open(image, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(upload_server_url, files=files)
        response.raise_for_status()
        uploaded_image = response.json()
        if not uploaded_image['photo']:
            raise Exception('Can\'t upload image')
        return uploaded_image


def save_image(params, image):
    """ post comics on group """
    params['photo'] = image['photo']
    params['server'] = image['server']
    params['hash'] = image['hash']
    response = requests.post(
        f'{VK_URL_METHOD}/photos.saveWallPhoto', params=params)
    response.raise_for_status()
    wall_photo = response.json()['response'][0]
    if 'error' in wall_photo:
        raise Exception(wall_photo['error']['error_msg'])
    return wall_photo


def post_image(params, comics, image):
    """ post comics on group """
    params['owner_id'] = -(int(params['group_id']))
    params['from_group'] = 1
    params['attachments'] = f'photo{image["owner_id"]}_{image["id"]}'
    params['message'] = comics['title']
    response = requests.post(
        f'{VK_URL_METHOD}/wall.post', params=params)
    response.raise_for_status()
    uploaded_wall_post = response.json()['response']
    if 'error' in uploaded_wall_post:
        raise Exception(uploaded_wall_post['error']['error_msg'])


def main():
    comics = None
    try:
        urllib3.disable_warnings()

        load_dotenv()
        VK_ACCESS_TOKEN = os.getenv('VK_ACCESS_TOKEN')
        VK_GROUP_ID = os.getenv('VK_GROUP_ID')

        params = {'group_id': VK_GROUP_ID,
                  'access_token': VK_ACCESS_TOKEN, 'v': '5.126'}

        comics = get_random_xkcd_comics()
        upload_server = get_upload_server(params)
        uploaded_image = upload_image(
            comics['image'], upload_server['upload_url'])
        saved_image = save_image(params, uploaded_image)
        post_image(params, comics, saved_image)

    except requests.exceptions.ConnectionError as conn_err:
        print(f"ConnectionError occured - {conn_err}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTPError occured - {http_err}")
    except Exception as err:
        print(f'Other error occured - {err}')

    finally:
        Path(comics['image']).unlink()


if __name__ == '__main__':
    main()
