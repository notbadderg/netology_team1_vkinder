import vk_api
from .utils.logger import logger

class VkUserApi:
    def __init__(self, vk_config):
        self._create_user_session(vk_config.user_token)

    def _create_user_session(self, token):
        """ Инициирует сессию с токеном пользователя """

        self.user_session = vk_api.VkApi(token=token)
        self.user_api = self.user_session.get_api()

    @logger()
    def find_users(self, birth_year=None, sex=None, city=None, fields=None, offset=0):
        """ Ищет пользователей по указанному фильтру """

        params = {
            'city': city,
            'sex': sex,
            'has_photo': '1',
            'fields': fields,
            'birth_year': birth_year,
            'offset': offset
        }

        resp = self.user_api.users.search(**params)

        return resp

    @logger()
    def get_photos_by_owner_id(self, owner_id, album_id='profile', extended=1):
        """ Получить фото по id пользователя """

        params = {
            'owner_id': owner_id,
            'album_id': album_id,
            'extended': extended
        }
        resp = self.user_api.photos.get(**params)

        return resp

    @logger()
    def get_photo_link(self, user_id):
        """ Получить ссылку на фото по id пользователя """
        
        photo = self.get_photos_by_owner_id(user_id)
        result = []

        for i, item in enumerate(sorted(photo['items'], key=lambda photo_: photo_['likes']['count'], reverse=True)):
            media_id = item['id']
            owner_id = item['owner_id']
            result.append((media_id, owner_id, f'photo{owner_id}_{media_id}'))
            if i == 2:
                return result

        return result
