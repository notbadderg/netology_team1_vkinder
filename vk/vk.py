import json

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vkinder.config import VkToken

class VkBot():
    def __init__(self, group_token, group_id, user_token):
        self.qwe = VkToken.group_token
        self._create_group_session(group_token, group_id)
        self._create_user_session(user_token)

    def _create_group_session(self, group_token, group_id):
        """ Инициирует сессию с токеном группы """

        self.group_session = vk_api.VkApi(token=group_token)
        self.longpoll = VkBotLongPoll(self.group_session, group_id)
        self.group_api = self.group_session.get_api()


    def _create_user_session(self, token):
        """ Инициирует сессию с токеном пользователя """


        self.user_session = vk_api.VkApi(token=token)
        self.user_api = self.user_session.get_api()

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
            result.append(f'photo{owner_id}_{media_id}')

            result.append(result.append(f'photo{owner_id}_{media_id}'))
            if i == 2:
                return result

    def user_generator(self, users):
        for user in users:
            if user['is_closed']:
                continue
            name = f'{user["first_name"]} {user["last_name"]}'
            ref = f'https://vk.com/id{user["id"]}'
            photo_link = self.get_photo_link(user["id"])
            yield name + '\n' + ref
            yield photo_link


    def listener(self):
        """ https://vk.com/dev/bots_longpoll """
        start_menu = self.get_start_menu()
        main_menu = self.get_main_menu()
        restart_menu = self.get_restart_menu()
        stop_menu = self.get_stop_menu()
        
        for event in self.longpoll.listen():            
            if event.type == VkBotEventType.MESSAGE_NEW:
                current_user = event.obj.message['from_id']
                current_message = event.obj.message['text']

                if current_message == 'Начать' or current_message == 'Перезапустить бота':
                    user_info = self.get_user_info(event.obj.message['from_id'], fields='bdate, sex, city')

                    if 'city' in user_info:
                        city = user_info['city']['id']
                    else:
                        city = None
                        self.send_message(current_user, 'Кажется, у вас не указан город!')

                    if user_info['sex'] == 1:
                        sex = 2
                    elif user_info['sex'] == 2:
                        sex = 1
                    else:
                        self.send_message(current_user, 'Кажется, у вас не указан пол!')

                    if 'bdate' in user_info and len(user_info['bdate'].split('.')) == 3:
                        birth_year = user_info['bdate'].split('.')[2]
                    else:
                        birth_year = None
                        self.send_message(current_user, 'Кажется, у вас не указан год рождения!')                     

                    if city is None or self == 0 or birth_year is None:
                        self.send_message(current_user, 'Измените настройки профиля и перезапустите бота!', keyboard=restart_menu)
                    else:
                        self.send_message(current_user, f'Ваш город (city_id): {city}')
                        self.send_message(current_user, f'Ваш пол: {"мужской" if sex == 1 else "женский"}')
                        self.send_message(current_user, f'Ваш год рождения: {birth_year}')
                        self.send_message(current_user, 'Давай знакомиться? Начни поиск!', keyboard=start_menu)

                elif current_message == 'Начать поиск':
                    self.send_message(current_user, 'Поиск запущен...', keyboard=main_menu)
                    users = self.find_users(birth_year, sex, city, fields='bdate, sex, city')
                    user_gen = self.user_generator(users['items'])
                    self.send_message(current_user, f'{next(user_gen)}', f'{",".join(next(user_gen))}')
                elif current_message == 'Продолжить поиск':
                    self.send_message(current_user, 'Продолжаю поиск...', keyboard=main_menu)
                    self.send_message(current_user, f'{next(user_gen)}', f'{",".join(next(user_gen))}')
                elif current_message == 'Добавить в избранное':
                    self.send_message(current_user, 'Данные обновлены', keyboard=main_menu)
                elif current_message == 'Показать избранное':
                    self.send_message(current_user, 'Избранное:', keyboard=main_menu)
                elif current_message == 'Остановить бота':
                    self.send_message(current_user, 'Бот остановлен', keyboard=stop_menu)                    

            else:
                print(event.type)
                print()


if __name__ == '__main__':
    VkBot(
        group_token='',
        group_id='',
        user_token=''
    ).listener()