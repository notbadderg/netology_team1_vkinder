import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.utils import get_random_id
from .utils.logger import logger

class VkGroupApi:
    def __init__(self, vk_config):
        self._create_group_session(vk_config.group_token, vk_config.group_id)

    def _create_group_session(self, group_token, group_id):
        """ Инициирует сессию с токеном группы  """

        self.group_session = vk_api.VkApi(token=group_token)
        self.long_poll = VkBotLongPoll(self.group_session, group_id)
        self.group_api = self.group_session.get_api()

    @logger()
    def get_user_info(self, user_id, fields=None):
        """ Получает информацию о пользователе """

        params = {
            'user_ids': user_id, 
            'fields': fields
        }
        resp = self.group_api.users.get(**params)

        return resp[0]

    @logger()
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
