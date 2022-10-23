from vk_api.bot_longpoll import VkBotEventType
from .vk_group_api import VkGroupApi
from .vk_user_api import VkUserApi
from .vk_menu_api import VkMenuApi
from .db.data_classes import DataClassesDBI, Photo, Target, TargetsList
from .db.db_interface import DatabaseInterface
from .utils.logger import logger


class VkBot(VkGroupApi, VkUserApi, VkMenuApi):
    def __init__(self, vk_config, db_config):
        super().__init__(vk_config)
        DataClassesDBI.dbi = DatabaseInterface(db_config)
        self._create_group_session(vk_config.group_token, vk_config.group_id)
        self._create_user_session(vk_config.user_token)
        self._init_menu()
        self.current_menu = None
        # Init current user params:
        self.city = None
        self.sex = None
        self.birth_year = None
        self.targets = None
        self.current_target = None
        self.find_offset = 0

    @logger()
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

    @logger()
    def check_user_info(self, current_user, user_info):
        if 'city' in user_info:
            self.city = user_info['city']['id']
        else:
            self.send_message(current_user, 'Кажется, у тебя не указан город!')

        if user_info['sex'] == 1:
            self.sex = 2
        elif user_info['sex'] == 2:
            self.sex = 1
        else:
            self.send_message(current_user, 'Кажется, у тебя не указан пол!')

        if 'bdate' in user_info and len(user_info['bdate'].split('.')) == 3:
            self.birth_year = user_info['bdate'].split('.')[2]
        else:
            self.send_message(current_user, 'Кажется, у тебя не указан год рождения!')

    @logger()
    def search_start_state(self, event, current_user):
        user_info = self.get_user_info(event.obj.message['from_id'], fields='bdate, sex, city')

        self.check_user_info(current_user, user_info)           

        if not (self.city and self.sex and self.birth_year):
            self.send_message(current_user, 'Измени настройки профиля и перезапусти бота!',
                              keyboard=self.restart_menu)
            self.current_menu = self.restart_menu
        else:
            self.send_message(current_user, f'Твой город (city_id): {self.city}')
            self.send_message(current_user, f'Твой пол: {"мужской" if self.sex == 1 else "женский"}')
            self.send_message(current_user, f'Твой год рождения: {self.birth_year}')
            self.send_message(current_user, 'Давай знакомиться? Начни поиск!', keyboard=self.start_menu)
            self.current_menu = self.start_menu
            return True

    @logger()
    def search_active_state(self, current_user):
        self.send_message(current_user, 'Начинаем поиск...')
        users = self.find_users(self.birth_year, self.sex, self.city, fields='bdate, sex, city')
        self.targets = self.create_obj(current_user, imitation_users_list_from_api=users)
        target = next(self.targets)
        self.current_target = target
        message = f'{target.first_name} {target.last_name}\n{target.url}'
        attachment = ",".join([photo.photo_link for photo in target.photos])
        self.send_message(current_user, message, attachment, keyboard=self.main_menu)
        self.current_menu = self.main_menu

    @logger()
    def search_continue_state(self, current_user):
        self.send_message(current_user, 'Продолжаю поиск...', keyboard=self.main_menu)
        try:
            target = next(self.targets)
        except StopIteration:
            self.find_offset += 15
            users = self.find_users(self.birth_year,
                                    self.sex, self.city,
                                    fields='bdate, sex, city',
                                    offset=self.find_offset)
            self.targets = self.create_obj(current_user, imitation_users_list_from_api=users)
            target = next(self.targets)            
        self.current_target = target
        message = f'{target.first_name} {target.last_name}\n{target.url}'
        attachment = ",".join([photo.photo_link for photo in target.photos])                    
        self.send_message(current_user, message, attachment)
        self.current_menu = self.main_menu

    @logger()
    def add_fav_state(self, current_user):
        self.current_target.add_favorite(current_user)
        self.send_message(current_user, 'Данные обновлены', keyboard=self.main_menu)
        self.current_menu = self.main_menu

    @logger()
    def show_fav_state(self, current_user):
        self.send_message(current_user, 'Избранное:', keyboard=self.main_menu)
        for fav in self.targets.get_favorites():
            message = f'{fav.first_name} {fav.last_name}\n{fav.url}'
            attachment = ",".join([photo.photo_link for photo in fav.photos])
            self.send_message(current_user, message, attachment, keyboard=self.main_menu)
        self.current_menu = self.main_menu

    @logger()
    def stop_state(self, current_user):
        self.send_message(current_user, 'Бот остановлен', keyboard=self.stop_menu)
        self.current_menu = self.stop_menu

    @logger()
    def incorrect_command_state(self, current_user):
        self.send_message(current_user, 'Пожалуйса, введи корректную команду!', keyboard=self.current_menu)

    def _listener(self):
        """ https://vk.com/dev/bots_longpoll """
        
        search_start_flag = False
        
        for event in self.long_poll.listen():
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
                    self.stop_state(current_user)
                else:
                    self.incorrect_command_state(current_user)

    def start(self):
        self._listener()
