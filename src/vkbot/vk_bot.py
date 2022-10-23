from vk_api.bot_longpoll import VkBotEventType
from .vk_group_api import VkGroupApi
from .vk_user_api import VkUserApi
from .vk_menu_api import VkMenuApi
from .db.data_classes import DataClassesDBI, Photo, Target, TargetsList
from .db.db_interface import DatabaseInterface
from .utils.logger import logger


class Client:
    def __init__(self, vk_id):
        self.vk_id = vk_id
        self.city = 3
        self.sex = None
        self.birth_year = None
        self.targets = None
        self.current_target = None
        self.current_menu = None
        self.find_offset = 0
        self.search_start_flag = False


class VkBot(VkGroupApi, VkUserApi, VkMenuApi):
    def __init__(self, vk_config, db_config):
        super().__init__(vk_config)
        DataClassesDBI.dbi = DatabaseInterface(db_config)
        self._create_group_session(vk_config.group_token, vk_config.group_id)
        self._create_user_session(vk_config.user_token)
        self._init_menu()
        self.clients = {}

    @logger()
    def create_obj(self, client_vk_id, users_list_from_api):
        targets = TargetsList(client_vk_id=client_vk_id)
        for user in users_list_from_api['items']:
            if user['is_closed']:
                continue
            target = Target(user['id'],
                            user['first_name'],
                            user['last_name'],
                            f'https://vk.com/id{user["id"]}')
            targets.append(target)

        return iter(targets)

    @logger()
    def get_photos_from_api(self, vk_id):
        temp_photos_list = []
        for photo_id, target_vk_id, photo_link in self.get_photo_link(vk_id):
            temp_photos_list.append(Photo(photo_id, target_vk_id, photo_link))
        return temp_photos_list

    @logger()
    def check_user_info(self, current_client, user_info):
        if 'city' in user_info:
            self.clients[current_client].city = user_info['city']['id']
        else:
            self.send_message(current_client, 'Кажется, у тебя не указан город!')

        if user_info['sex'] == 1:
            self.clients[current_client].sex = 2
        elif user_info['sex'] == 2:
            self.clients[current_client].sex = 1
        else:
            self.send_message(current_client, 'Кажется, у тебя не указан пол!')

        if 'bdate' in user_info and len(user_info['bdate'].split('.')) == 3:
            self.clients[current_client].birth_year = user_info['bdate'].split('.')[2]
        else:
            self.send_message(current_client, 'Кажется, у тебя не указан год рождения!')

    @logger()
    def search_start_state(self, event, current_client):
        user_info = self.get_user_info(event.obj.message['from_id'], fields='bdate, sex, city')

        self.check_user_info(current_client, user_info)

        if not (self.clients[current_client].city and
                self.clients[current_client].sex and
                self.clients[current_client].birth_year):
            self.send_message(current_client, 'Измени настройки профиля и перезапусти бота!',
                              keyboard=self.restart_menu)
            self.clients[current_client].current_menu = self.restart_menu
            self.clients[current_client].search_start_flag = False
            return None
        else:
            self.send_message(current_client, f'Твой город (city_id): {self.clients[current_client].city}')
            self.send_message(current_client, f'Твой пол: {"М" if self.clients[current_client].sex == 1 else "Ж"}')
            self.send_message(current_client, f'Твой год рождения: {self.clients[current_client].birth_year}')
            self.send_message(current_client, 'Давай знакомиться? Начни поиск!', keyboard=self.start_menu)
            self.clients[current_client].current_menu = self.start_menu
            self.clients[current_client].search_start_flag = True
            return None

    @logger()
    def search_active_state(self, current_client):
        self.send_message(current_client, 'Начинаем поиск...')
        users = self.find_users(self.clients[current_client].birth_year,
                                self.clients[current_client].sex,
                                self.clients[current_client].city,
                                fields='bdate, sex, city',
                                offset=0, count=15)
        self.clients[current_client].targets = self.create_obj(current_client, users_list_from_api=users)
        target = next(self.clients[current_client].targets)
        self.clients[current_client].current_target = target
        target.photos = self.get_photos_from_api(target.vk_id)
        message = f'{target.first_name} {target.last_name}\n{target.url}'
        attachment = ",".join([photo.photo_link for photo in target.photos])
        self.send_message(current_client, message, attachment, keyboard=self.main_menu)
        self.clients[current_client].current_menu = self.main_menu

    @logger()
    def search_continue_state(self, current_client):
        self.send_message(current_client, 'Продолжаю поиск...', keyboard=self.main_menu)
        target = next(self.clients[current_client].targets)
        if target == 0:
            self.clients[current_client].find_offset += 15
            users = self.find_users(self.clients[current_client].birth_year,
                                    self.clients[current_client].sex, self.clients[current_client].city,
                                    fields='bdate, sex, city',
                                    offset=self.clients[current_client].find_offset,
                                    count=15)
            self.clients[current_client].targets = self.create_obj(current_client, users_list_from_api=users)
            if not self.clients[current_client].targets.targets:
                self.send_message(current_client, 'Похоже, что больше никого нет.', keyboard=self.main_menu)
                self.clients[current_client].current_menu = self.main_menu
                return None
            else:
                target = next(self.clients[current_client].targets)
        self.clients[current_client].current_target = target
        target.photos = self.get_photos_from_api(target.vk_id)
        message = f'{target.first_name} {target.last_name}\n{target.url}'
        attachment = ",".join([photo.photo_link for photo in target.photos])
        self.send_message(current_client, message, attachment)
        self.clients[current_client].current_menu = self.main_menu

    @logger()
    def add_fav_state(self, current_client):
        self.clients[current_client].current_target.add_favorite(current_client)
        self.send_message(current_client, 'Данные обновлены', keyboard=self.main_menu)
        self.clients[current_client].current_menu = self.main_menu

    @logger()
    def show_fav_state(self, current_client):
        self.send_message(current_client, 'Избранное:', keyboard=self.main_menu)
        favorites = self.clients[current_client].targets.get_favorites()
        if len(favorites) == 0:
            self.send_message(current_client, 'Список пока пуст.', keyboard=self.start_menu)
        else:
            for fav in favorites:
                message = f'{fav.first_name} {fav.last_name}\n{fav.url}'
                attachment = ",".join([photo.photo_link for photo in fav.photos])
                self.send_message(current_client, message, attachment, keyboard=self.main_menu)
        self.clients[current_client].current_menu = self.main_menu

    @logger()
    def stop_state(self, current_client):
        self.send_message(current_client, 'Бот остановлен', keyboard=self.stop_menu)
        self.clients[current_client].current_menu = self.stop_menu

    @logger()
    def incorrect_command_state(self, current_client):
        self.send_message(current_client, 'Пожалуйса, введи корректную команду!', keyboard=self.current_menu)

    def _listener(self):
        """ https://vk.com/dev/bots_longpoll """

        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                self._show_active_users()
                current_client = event.obj.message['from_id']
                current_message = event.obj.message['text']
                if current_client not in self.clients.keys():
                    self.clients[current_client] = Client(current_client)
                if current_message == 'Начать' or current_message == 'Перезапустить бота':
                    self.search_start_state(event, current_client)
                elif current_message == 'Начать поиск' and self.clients[current_client].search_start_flag:
                    self.search_active_state(current_client)
                elif current_message == 'Продолжить поиск' and self.clients[current_client].search_start_flag:
                    self.search_continue_state(current_client)
                elif current_message == 'Добавить в избранное' and self.clients[current_client].search_start_flag:
                    self.add_fav_state(current_client)
                elif current_message == 'Показать избранное' and self.clients[current_client].search_start_flag:
                    self.show_fav_state(current_client)
                elif current_message == 'Остановить бота':
                    self.stop_state(current_client)
                else:
                    self.incorrect_command_state(current_client)

    def _show_active_users(self):
        print(f'ACTIVE USERS: {len(self.clients)}')
        for n, client in enumerate(self.clients):
            print(f'{n} - {client}', end='')
        print()

    def start(self):
        self._listener()
