import vkinder.data_classes as dc
import db_interface 


class DatabaseConnector:
    def __init__(self, idclient):
        """
        idclient - ID пользователя
        """
        self.idclient = idclient

    def addfav(self, id_target, name_target, url_target, target_photos: list, surname_target=''):
        """
        Добавление понравившегося пользователя в избранное пользователя.
        Обязательные поля:
        id_target - ID понравившегося пользователя,
        name_target - имя понравившегося пользователя,
        url_target - ссылка понравившегося пользователя,
        target_photos - список словарей [{'url': 'https://1.jpg', 'likes': 0},
                         {'url': 'https://2.jpg', 'likes': 10},
                         {'url': 'https://3.jpg', 'likes': 100}] 
        Необязательные поля:
        surname_target - фамилия понравившегося пользователя.
        """

        fav = dc.Favorite(self.idclient, id_target)
        target = dc.Target(id_target, name_target, surname_target, url_target)
        photos_list = []
        for photo in target_photos:
            p = dc.Photo(id_target, photo['url'], photo['likes'])
            photos_list.append(p)   # Добавляет объект фото в список объекта фотолист

        dbi = db_interface.DatabaseInterface()
        result_target = dbi.insert(target)
        result_fav = dbi.insert(fav)
        result_photos_list = dbi.insert(photos_list)
        
        if result_fav or result_target or result_photos_list: 
            return True
        return False

    def getfav(self):
        """
        Получение списка избранного по клиенту
        """

        dbi = db_interface.DatabaseInterface()
        favorite_list = dbi.select_client_favorite_with_photo(self.idclient)
        if len(favorite_list.favorites) == 0:
            return 'нет избранных'

        result = ''
        for favorite in favorite_list:
            result += (
                    f'{favorite.name} {favorite.surname}\n'
                    f'{favorite.url}\n'
                    f'{favorite.photos_list}\n'
                    )
        return result

