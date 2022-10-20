class Photo:
    def __init__(self, photo_id: int, target_vk_id: int):
        self.photo_id = photo_id
        self.target_vk_id = target_vk_id


class Target:
    def __init__(self, vk_id: int, first_name: str, last_name: str, url: str, database_interface=None):
        self.vk_id = vk_id
        self.first_name = first_name
        self.last_name = last_name
        self.url = url
        self.photos = []
        self.dbi = database_interface

    def add_favorite(self, client_vk_id: int):
        self.dbi.add_to_favorite(self, client_vk_id)
        return None


class TargetsList:
    def __init__(self, client_vk_id: int, database_interface=None):
        self.client_vk_id = client_vk_id
        self.targets = []
        self.dbi = database_interface

    def __iter__(self):
        self.cursor = -1
        return self

    def __next__(self):
        self.cursor += 1
        if self.cursor == len(self.targets):
            raise StopIteration
        return self.targets[self.cursor]

    def append(self, element: Target):
        self.targets.append(element)
        return None

    def get_favorites(self) -> list:
        return self.dbi.get_client_favorites_list(self.client_vk_id)
