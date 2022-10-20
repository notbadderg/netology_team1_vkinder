import os
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
        self.launch_drop = os.getenv('DB_DROP_TABLES_AFTER_LAUNCH')


class VkTokensList(Config):
    group_token = os.getenv('VK_GROUP_TOKEN')
    user_token = os.getenv('VK_USER_TOKEN')



