import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from vkbot.db.data_classes import DataClassesDBI, Photo, Target, TargetsList
from vkbot.db.db_interface import DatabaseInterface


class VkBot():
    def __init__(self, vk_config, db_config):
        DataClassesDBI.dbi = DatabaseInterface(db_config)      
        self._create_group_session(vk_config.group_token, vk_config.group_id)
        self._create_user_session(vk_config.user_token)
        self._init_current_user_param()
        self._init_menu()

    def _create_group_session(self, group_token, group_id):
        """ Инициирует сессию с токеном группы  """

        self.group_session = vk_api.VkApi(token=group_token)
        self.longpoll = VkBotLongPoll(self.group_session, group_id)
        self.group_api = self.group_session.get_api()

    def _create_user_session(self, token):
        """ Инициирует сессию с токеном пользователя """

        self.user_session = vk_api.VkApi(token=token)
        self.user_api = self.user_session.get_api()

    def _init_current_user_param(self):
        self.city = None
        self.sex = None
        self.birth_year = None
        self.targets = None
        self.curent_target = None

    def _init_menu(self):
        self.start_menu = self.get_start_menu()
        self.restart_menu = self.get_restart_menu()        
        self.main_menu = self.get_main_menu()

    def get_start_menu(self):
        """ Начальное меню """

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Начать поиск', color=VkKeyboardColor.POSITIVE)

        return keyboard.get_keyboard()

    def get_main_menu(self):
        """ Основное меню """

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Продолжить поиск', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Добавить в избранное', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Показать избранное', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Остановить бота', color=VkKeyboardColor.NEGATIVE)

        return keyboard.get_keyboard()        

    def get_restart_menu(self):
        """ Меню перезапуска бота """

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Перезапустить бота', color=VkKeyboardColor.POSITIVE)

        return keyboard.get_keyboard()

    def get_stop_menu(self):
        """ Меню после остановки бота """

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Начать', color=VkKeyboardColor.PRIMARY)

        return keyboard.get_keyboard()

    def get_user_info(self, user_id, fields=None):
        """ Получает информацию о пользователе """

        params = {
            'user_ids': user_id, 
            'fields': fields
        }
        resp = self.group_api.users.get(**params)

        return resp[0]

    def find_users(self, birth_year=None, sex=None, city=None, fields=None):
        """ Ищет пользователей по указанному фильтру """

        params = {
            'city': city,
            'sex': sex,
            'has_photo': '1',
            'fields': fields,
            'birth_year': birth_year
        }

        resp = self.user_api.users.search(**params)

        return resp

    def send_message(self, user_id, text, attachment=None, keyboard=None):
        """ Отправляет сообщение пользователю """

        params = {
            'user_id': user_id,
            'message': text,
            'random_id': get_random_id(),
            'keyboard': keyboard,
            'attachment': attachment
        }
        message_id = self.group_api.messages.send(**params)

        return message_id

    def get_photos_by_owner_id(self, owner_id, album_id='profile', extended=1):
        """ Получить фото по id пользователя """

        params = {
            'owner_id': owner_id,
            'album_id': album_id,
            'extended': extended
        }
        resp = self.user_api.photos.get(**params)

        return resp

    def get_photo_link(self, user_id):
        photo = self.get_photos_by_owner_id(user_id)
        result = []

        for i, item in enumerate(sorted(photo['items'], key=lambda photo: photo['likes']['count'], reverse=True)):
            media_id = item['id']
            owner_id = item['owner_id']
            result.append((media_id, owner_id, f'photo{owner_id}_{media_id}'))
            if i == 2:
                return result

        return result

    def create_obj(self, client_vk_id, imitation_users_list_from_api):
        targets = TargetsList(client_vk_id=client_vk_id)
        for user in imitation_users_list_from_api['items']:
            if user['is_closed']:
                continue    
            target = Target(user['id'],
                            user['first_name'],
                            user['last_name'],
                            f'https://vk.com/id{user["id"]}')

            for photo_id, target_vk_id, photo_link in self.get_photo_link(target.vk_id):
                target.photos.append(Photo(photo_id, target_vk_id, photo_link))
            targets.append(target)

        return iter(targets)

    def get_opposite_sex(self, sex):
        sex = sex - 1 if sex == 2 else sex + 1
        return sex
        
    def search_start_state(self, event, current_user):
        user_info = self.get_user_info(event.obj.message['from_id'], fields='bdate, sex, city')

        if 'city' in user_info:
            self.city = user_info['city']['id']
        else:
            self.send_message(current_user, 'Кажется, у вас не указан город!')

        if user_info['sex'] == 1:
            self.sex = 2
        elif user_info['sex'] == 2:
            self.sex = 1
        else:
            self.send_message(current_user, 'Кажется, у вас не указан пол!')

        if 'bdate' in user_info and len(user_info['bdate'].split('.')) == 3:
            self.birth_year = user_info['bdate'].split('.')[2]
        else:
            self.send_message(current_user, 'Кажется, у вас не указан год рождения!')                     

        if not (self.city and self.sex and self.birth_year):
            self.send_message(current_user, 'Измените настройки профиля и перезапустите бота!', keyboard=self.restart_menu)
        else:
            self.send_message(current_user, f'Ваш город (city_id): {self.city}')
            self.send_message(current_user, f'Ваш пол: {"мужской" if self.sex == 1 else "женский"}')
            self.send_message(current_user, f'Ваш год рождения: {self.birth_year}')
            self.send_message(current_user, 'Давай знакомиться? Начни поиск!', keyboard=self.start_menu)
            return True

    def search_active_state(self, current_user):
        self.send_message(current_user, 'Поиск запущен...')
        users = self.find_users(self.birth_year, self.sex, self.city, fields='bdate, sex, city')
        self.targets = self.create_obj(current_user, imitation_users_list_from_api=users)
        target = next(self.targets)
        self.curent_target = target
        message = f'{target.first_name} {target.last_name}\n{target.url}'
        attachment = ",".join([photo.photo_link for photo in target.photos])
        self.send_message(current_user, message, attachment, keyboard=self.main_menu)

    def search_continue_state(self, current_user):
        self.send_message(current_user, 'Продолжаю поиск...', keyboard=self.main_menu)
        target = next(self.targets)
        self.curent_target = target
        message = f'{target.first_name} {target.last_name}\n{target.url}'
        attachment = ",".join([photo.photo_link for photo in target.photos])                    
        self.send_message(current_user, message, attachment)

    def add_fav_state(self, current_user):
        self.curent_target.add_favorite(current_user)
        self.send_message(current_user, 'Данные обновлены', keyboard=self.main_menu)

    def show_fav_state(self, current_user):
        self.send_message(current_user, 'Избранное:', keyboard=self.main_menu)
        for fav in self.targets.get_favorites():
            message = f'{fav.first_name} {fav.last_name}\n{fav.url}'
            attachment = ",".join([photo.photo_link for photo in fav.photos])
            self.send_message(current_user, message, attachment, keyboard=self.main_menu)

    def _listener(self):
        """ https://vk.com/dev/bots_longpoll """
        
        search_start_flag = False
        stop_menu = self.get_stop_menu()

        for event in self.longpoll.listen():            
            if event.type == VkBotEventType.MESSAGE_NEW:
                current_user = event.obj.message['from_id']
                current_message = event.obj.message['text']

                if current_message == 'Начать' or current_message == 'Перезапустить бота':
                    search_start_flag = self.search_start_state(event, current_user)
                elif current_message == 'Начать поиск' and search_start_flag:
                    self.search_active_state(current_user)
                elif current_message == 'Продолжить поиск' and search_start_flag:
                    self.search_continue_state(current_user)
                elif current_message == 'Добавить в избранное' and search_start_flag:
                    self.add_fav_state(current_user)
                elif current_message == 'Показать избранное' and search_start_flag:
                    self.show_fav_state(current_user)
                elif current_message == 'Остановить бота':
                    self.send_message(current_user, 'Бот остановлен', keyboard=stop_menu)
            else:
                print(event.type)
                print()

    def start(self):
        self._listener()
        #########









        #FOR QUICK DB TESTING
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
                    target.photos.append(Photo(photo_id=photo['id'],
                                               target_vk_id=photo['owner_id'],
                                               photo_link='sample_link'))
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
        # test_db()
