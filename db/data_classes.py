class Photo:
    def __init__(self, photo_id: int, target_vk_id: int):
        self.photo_id = photo_id
        self.target_vk_id = target_vk_id


class Target:
    def __init__(self, vk_id: int, first_name: str, last_name: str, url: str, dbi=None):
        self.vk_id = vk_id
        self.first_name = first_name
        self.last_name = last_name
        self.url = url
        self.photos = []
        self.dbi = dbi

    def add_favorite(self, client_vk_id: int):
        self.dbi.add_to_favorite(self, client_vk_id)
        return None


class TargetsList:
    def __init__(self, client_vk_id: int, dbi=None):
        self.client_vk_id = client_vk_id
        self.targets = []
        self.cursor = -1
        self.dbi = dbi

    def __iter__(self):
        return self

    def __next__(self):
        self.cursor += 1
        if self.cursor == len(self.targets):
            raise StopIteration
        return self.targets[self.cursor]

    def append(self, element: Target):
        self.targets.append(element)
        return None

    def get_favorites(self):
        return self.dbi.get_client_favorites_list(self.client_vk_id)
