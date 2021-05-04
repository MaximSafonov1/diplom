from pprint import pprint
import requests
from datetime import datetime
import time
from tqdm import tqdm

token = input('Введите VK токен: ')

class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.token = token
        self.version = version
        self.params = {
            'access_token': self.token,
            'v': self.version
        }
        self.owner_id = requests.get(self.url + 'users.get', self.params).json()['response'][0]['id']

    def get_photos(self, user_id=None, count=100):
        if user_id is None:
            user_id = self.owner_id
        followers_url = self.url + 'photos.get'
        followers_params = {
            'count': count,
            'user_id': user_id,
            'album_id': 'profile',
            'extended': 1
        }
        res = requests.get(followers_url, params={**self.params, **followers_params})
        return res.json()

    def max_size(self, user_id=None, count=100):
        if user_id is None:
            user_id = self.owner_id
        photos_list = []
        all_photos = self.get_photos(user_id, count)
        for photo in all_photos['response']['items']:
            photos_list.append({
                'likes': photo['likes']['count'],
                'url': photo['sizes'][-1]['url'],
                'size': photo['sizes'][-1]['type']
            })
        print(f'Всего на странице: {len(photos_list)} фото.')
        return photos_list


id = input('Введите id пользователя или нажмите enter для определения id по токену: ')

vk_client = VkUser(token, '5.130')

vk_photos = vk_client.max_size(id)

# pprint(vk_photos)
# pprint(vk_client.get_photos(id))


ya_token = input('Введите Я.Диск токен: ')

class YaUploader:

    def __init__(self, token):
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def create_folder(self, folder_name):
        file_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {
            'path': folder_name
        }
        response = requests.put(file_url, headers=self.headers, params=params)
        return response.json()

    def get_files_list(self):
        file_url = 'https://cloud-api.yandex.net/v1/disk/resources/files'
        response = requests.get(file_url, headers=self.headers)
        return response.json()

    def load_url(self, file_path, file_name):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        params = {
            'url': file_path,
            'path': file_name
        }
        response = requests.post(upload_url, headers=self.headers, params=params)
        if response.status_code == 202:
            print('success')
        else:
            print('error')
        return response

    def save_photos(self, vk_photos, count=5):
        folder_name = datetime.strftime(datetime.now(), "%d.%m.%Y-%H.%M.%S")
        self.create_folder(folder_name)
        json_file = []
        for item in tqdm(vk_photos[0:count]):
            full_name = f"{folder_name}/{item['likes']}.jpg"
            result = self.load_url(item['url'], full_name)
            json_file.append({'file_name': full_name, 'size': item['size']})
            time.sleep(1)
        pprint(json_file)
        return result

count = int(input('Введите число фотографий, которые хотите загрузить на ЯндексДиск: '))

file = YaUploader(ya_token)
file.save_photos(vk_photos, count)


