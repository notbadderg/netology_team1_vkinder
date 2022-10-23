import vk_api

from .utils.logger import logger


class VkUserApi:
    """Класс VkUserApi используется для взаимодействия с Vkontakte c токеном пользователя

    Атрибуты
    ----------
    file_path : str
        полный путь до текстового файла
    lines : list
        список строк исходного файла

    Методы
    -------
    _create_user_session(token)
        Инициирует сессию с токеном пользователя
    find_users(client=None, fields=None, count=15)
        Найти пользователей по указанному фильтру
    get_photos_by_owner_id(owner_id, album_id='profile', extended=1)
        Получить фото по id пользователя
    get_photo_link(user_id)
        Получить ссылку на фото по id пользователя
    get_city_by_id(city_id):
        Получить название города по его id
    """

    def __init__(self, vk_config):
        self._create_user_session(vk_config.user_token)

    def _create_user_session(self, token):
        """Инициирует сессию с токеном пользователя.

        Ключевые аргументы:
        token -- токен пользователя
        """

        self.user_session = vk_api.VkApi(token=token)
        self.user_api = self.user_session.get_api()

    @logger()
    def find_users(self, client=None, fields=None, count=15):
        """Найти пользователей по указанному фильтру

        Ключевые аргументы:
        client -- экзмепляр класса Client с описанием параметров пользователя (по умолчанию None)
        fields -- список дополнительных полей профилей, которые необходимо вернуть
            (по умолчанию None)
        count -- количество возвращаемых пользователей (по умолчанию 15)
        """

        params = {
            'city': client.city,
            'sex': client.sex,
            'has_photo': '1',
            'fields': fields,
            'birth_year': client.birth_year,
            'offset': client.find_offset,
            'count': count
        }
        resp = self.user_api.users.search(**params)

        return resp

    # @logger()
    def get_photos_by_owner_id(self, owner_id, album_id='profile', extended=1):
        """Получить фото по id пользователя

        Ключевые аргументы:
        owner_id -- идентификатор владельца альбома
        album_id -- идентификатор альбома (по умолчанию profile)
        extended -- если 1, будут возвращены дополнительные поля likes, comments, tags,
            can_comment, reposts (по умолчанию 1)
        """

        params = {
            'owner_id': owner_id,
            'album_id': album_id,
            'extended': extended
        }
        resp = self.user_api.photos.get(**params)

        return resp

    @logger()
    def get_photo_link(self, user_id):
        """Получить ссылку на фото по id пользователя

        Ключевые аргументы:
        user_id -- идентификатор пользователя
        """

        photo = self.get_photos_by_owner_id(user_id)
        result = []
        sorted_photo = sorted(photo['items'],
                              key=lambda photo_: photo_['likes']['count'],
                              reverse=True)
        for i, item in enumerate(sorted_photo):
            media_id = item['id']
            owner_id = item['owner_id']
            result.append((media_id, owner_id, f'photo{owner_id}_{media_id}'))
            if i == 2:
                return result

        return result

    @logger()
    def get_city_by_id(self, city_id):
        """Получить название города по его id

        Ключевые аргументы:
        city_id -- идентификатор города
        """

        params = {
            'city_ids': city_id
        }
        resp = self.user_api.database.getCitiesById(**params)

        return resp[0]['title']
