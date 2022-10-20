from db.data_classes import Photo, Target, TargetsList


class VkBot:
    def __init__(self, dbi, vk_token):
        self.dbi = dbi
        self.group_token = vk_token.group_token
        self.user_token = vk_token.user_token

    def start(self):

        ############
        def test_db():
            ###FIXTURES:
            client_vk_id = 101
            imitation_users_list_from_api = [{'id': 123, 'first_name': 'Daria', 'last_name': 'Lavrova'}]
            imitation_user_123_photos_from_api = [{'id': 111, 'owner_id': 123},
                                                  {'id': 112, 'owner_id': 123}]

            #обрабатываем полученную инфу с апи чтобы сформировать объекты
            targets = TargetsList(client_vk_id=client_vk_id, dbi=self.dbi)
            for user in imitation_users_list_from_api:
                target = Target(user['id'], user['first_name'], user['last_name'], 'sample_ulr', dbi=self.dbi)
                for photo in imitation_user_123_photos_from_api:
                    target.photos.append(Photo(photo_id=photo['id'], target_vk_id=photo['owner_id']))
                targets.append(target)

            #показываем по очереди фото из targets клиенту:
            #через next или через цикл
            for target in targets:
                print(target.first_name)

            #если хотим добавить текущую цель в избранное (сразу в бд) надо лишь прописать:
                target.add_favorite(client_vk_id=client_vk_id)

            #если хотим получить список избранного, также через TargetsList работаем:
            favorites = targets.get_favorites()

            # показываем точно также как и в начале
            for favorite in favorites:
                print(favorite.first_name)
                print(favorite.photos)
                # достаем фотки:
                for photo in favorite.photos:
                    print(photo.photo_id)
        test_db()

