from config import VkConfig
from vkbot.vk_bot import VkBot


def main():
    vk_cfg = VkConfig()
    vkb = VkBot(vk_cfg)
    vkb.start()


if __name__ == "__main__":
    main()
