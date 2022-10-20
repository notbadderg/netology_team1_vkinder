from config import DatabaseConfig, VkTokensList
from src.vk_bot import VkBot


def main():
    db_cfg = DatabaseConfig()
    tokens = VkTokensList()

    vkb = VkBot(tokens, db_cfg)
    vkb.start()


if __name__ == "__main__":
    main()
