import os
from tokenize import group
from dotenv import find_dotenv, load_dotenv


class Config:
    load_dotenv(find_dotenv())


class DatabaseConfig(Config):
    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.port = os.getenv('DB_PORT')
        self.name = os.getenv('DB_NAME')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.launch_drop = _str_to_bool_convert(os.getenv('DB_RE_CREATE_TABLES_AFTER_LAUNCH'))
        self.echo = _str_to_bool_convert(os.getenv('DB_ECHO'))


class VkConfig(Config):
    group_id = os.getenv('VK_GROUP_ID')
    group_token = os.getenv('VK_GROUP_TOKEN')
    user_token = os.getenv('VK_USER_TOKEN')


def _str_to_bool_convert(string):
    if string == 'True':
        return True
    elif string == 'False':
        return False
    else:
        raise Exception(f'Wrong parameter "{string}"')
