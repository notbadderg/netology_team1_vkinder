class DataClassesList:
    class Target:
        def __init__(self, vk_id: int, name: str, surname: str, url: str):
            self.vk_id = vk_id
            self.name = name
            self.surname = surname
            self.url = url

    class Favorite:
        def __init__(self, client_vk_id: int, target_vk_id: int):
            self.client_vk_id = client_vk_id
            self.target_vk_id = target_vk_id

    class Photo:
        def __init__(self, owner_id: int, id: int):
            self.owner_id = owner_id
            self.id = id

    class FavoritesList:
        def __init__(self, favorites: list):
            self.favorites = favorites

        def __iter__(self):
            self.cursor = -1
            return self

        def __next__(self):
            self.cursor += 1
            if self.cursor == len(self.favorites):
                raise StopIteration
            return self.favorites[self.cursor]


if __name__ == '__main__':
    sample_targets_2 = [Target(1, 'Сергей', 'Петров', 'https://serega.mvp'),
                        Target(10, 'Екатерина', 'Смирнова', 'https://katuha.yo'),
                        Target(101, 'Захар', 'Иванов', 'https://ivanov.org')]
    test_favorite_list = FavoritesList(sample_targets_2)
    for e in test_favorite_list:
        print(e.name)
