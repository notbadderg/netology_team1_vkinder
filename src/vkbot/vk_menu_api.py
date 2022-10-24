from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class VkMenuApi:
    def __init__(self):
        self._init_menu()

    def _init_menu(self):
        self.start_menu = self.get_start_menu()
        self.restart_menu = self.get_restart_menu()
        self.main_menu = self.get_main_menu()
        self.stop_menu = self.get_stop_menu()
        self.search_finish_menu = self.get_search_finish_menu()
        self.current_menu = None

    @staticmethod
    def get_start_menu():
        """ Начальное меню """

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Начать поиск', color=VkKeyboardColor.POSITIVE)

        return keyboard.get_keyboard()

    @staticmethod
    def get_main_menu():
        """ Основное меню """

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Продолжить поиск', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Добавить в избранное', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Показать избранное', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Остановить бота', color=VkKeyboardColor.NEGATIVE)

        return keyboard.get_keyboard()        

    @staticmethod
    def get_restart_menu():
        """ Меню перезапуска бота """

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Перезапустить бота', color=VkKeyboardColor.POSITIVE)

        return keyboard.get_keyboard()

    @staticmethod
    def get_stop_menu():
        """ Меню после остановки бота """

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Начать', color=VkKeyboardColor.PRIMARY)

        return keyboard.get_keyboard()

    @staticmethod
    def get_search_finish_menu():
        """ Меню после исчерпания вариантов поиска """

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Начать сначала', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Показать избранное', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Остановить бота', color=VkKeyboardColor.NEGATIVE)

        return keyboard.get_keyboard()
