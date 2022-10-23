from config import VkConfig, DatabaseConfig
from vkbot.vk_bot import VkBot


def main():
    vk_cfg = VkConfig()
    db_config = DatabaseConfig()
    vkb = VkBot(vk_cfg, db_config)
    vkb.start()


if __name__ == "__main__":
    main()
