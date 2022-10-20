from config import DatabaseConfig, VkToken
from db.db_interface import DatabaseInterface
from vk.vk_bot import VkBot


def main():
    db_cfg = DatabaseConfig()
    vk_token = VkToken()
    dbi = DatabaseInterface(db_cfg)
    vkb = VkBot(dbi, vk_token)
    vkb.start()


if __name__ == "__main__":
    main()
