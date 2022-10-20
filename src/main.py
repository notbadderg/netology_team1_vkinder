from config import DatabaseConfig, VkConfig
from vkbot.vk_bot import VkBot


def main():
    db_cfg = DatabaseConfig()
    vk_cfg = VkConfig()

    vkb = VkBot(vk_cfg, db_cfg)
    vkb.start()


if __name__ == "__main__":
    main()
