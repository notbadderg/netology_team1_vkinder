from src.vkbot.db.data_classes import DataClassesDBI, Photo, Target, TargetsList
from src.vkbot.db.db_interface import DatabaseInterface


class VkBot:
    def __init__(self, vk_config, db_config):
        DataClassesDBI.dbi = DatabaseInterface(db_config)
        self.group_token = vk_config.group_token
        self.user_token = vk_config.user_token

    def start(self):
        #########
        def test_db():
            # ##FIXTURES:
            client_vk_id = 110
            imitation_users_list_from_api = [{'id': 200, 'first_name': 'Daria99', 'last_name': 'Lavrova99'}]
            imitation_user_photos_from_api = [{'id': 2002, 'owner_id': 200},
                                              {'id': 2003, 'owner_id': 200}]

            # обрабатываем полученную инфу с апи чтобы сформировать объекты
            targets = TargetsList(client_vk_id=client_vk_id)
            for user in imitation_users_list_from_api:
                target = Target(user['id'],
                                user['first_name'],
                                user['last_name'],
                                'sample_url')

                for photo in imitation_user_photos_from_api:
                    target.photos.append(Photo(photo_id=photo['id'], target_vk_id=photo['owner_id']))
                targets.append(target)

            # показываем по очереди фото из targets клиенту:
            # через next или через цикл
            for target in targets:
                print(target.first_name)

            # если хотим добавить текущую цель в избранное (сразу в бд) надо лишь прописать:
                result = target.add_favorite(client_vk_id=client_vk_id)
                if result:
                    print('Добавлено')
                else:
                    print('Не добавлено или уже добавлено')

            # если хотим получить список избранного, также через TargetsList работаем:
            favorites = targets.get_favorites()

            # показываем точно также как и в начале
            for favorite in favorites:
                print(favorite.first_name)
                print(favorite.photos)
                # достаем фотки:
                for photo in favorite.photos:
                    print(photo.photo_id)
        test_db()

