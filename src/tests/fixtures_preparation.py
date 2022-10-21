from src.vkbot.db.data_classes import Photo, Target, TargetsList


def fixtures_good():
    client_vk_id = 2100000000
    users = [{'id': 2100000001, 'first_name': 'Test1', 'last_name': 'Test1'},
             {'id': 2100000002, 'first_name': 'Test2', 'last_name': 'Test2'},
             {'id': 2100000003, 'first_name': 'Test3', 'last_name': 'Test3'},
             {'id': 2100000004, 'first_name': 'Test4', 'last_name': 'Test4'},
             {'id': 2100000005, 'first_name': 'Test5', 'last_name': 'Test5'}]

    photos = {2100000001: [{'id': 2000000001, 'owner_id': 2100000001},
                           {'id': 2000000002, 'owner_id': 2100000001}],
              2100000002: [{'id': 2000000003, 'owner_id': 2100000002},
                           {'id': 2000000004, 'owner_id': 2100000002}],
              2100000003: [{'id': 2000000005, 'owner_id': 2100000003},
                           {'id': 2000000006, 'owner_id': 2100000003}],
              2100000004: [{'id': 2000000007, 'owner_id': 2100000004},
                           {'id': 2000000008, 'owner_id': 2100000004}],
              2100000005: [{'id': 2000000009, 'owner_id': 2100000005},
                           {'id': 2000000010, 'owner_id': 2100000005}],
              }
    return {'client_vk_id': client_vk_id, 'users': users, 'photos': photos}


def fixtures_preparation(client_vk_id, users, photos):
    targets = TargetsList(client_vk_id=client_vk_id)
    for user in users:
        target = Target(user['id'],
                        user['first_name'],
                        user['last_name'],
                        'sample_url')

        for photo in photos[target.vk_id]:
            target.photos.append(Photo(photo_id=photo['id'],
                                       target_vk_id=photo['owner_id'],
                                       photo_link='sample_link'))
        targets.append(target)
    return targets


# if __name__ == '__main__':
#     t = fixtures_preparation(**fixtures_good())
#     print(t.targets[0].vk_id)
