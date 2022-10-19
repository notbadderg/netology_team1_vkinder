import sqlalchemy as sq
import sqlalchemy.exc
from sqlalchemy.orm import Session
from db.models import create_tables as ct, drop_tables as dt, FavoriteTable, TargetTable, PhotoTable
from data_classes import Target, Photo, Favorite, FavoritesList


class DatabaseInterface:
    def __init__(self, db_cfg):
        self.host = db_cfg.host
        self.port = db_cfg.port
        self.password = db_cfg.password
        self.user = db_cfg.user
        self.name = db_cfg.name
        self.launch_drop = db_cfg.launch_drop
        self.engine = sq.create_engine(self._make_dsn())
        self.create_table()

    def _make_dsn(self) -> str:
        driver = "postgresql://"
        credentials = f"{self.user}:{self.password}"
        address = f"{self.host}:{self.port}"
        db_name = self.name
        return f"{driver}{credentials}@{address}/{db_name}"

    def _drop_table(self) -> None:
        dt(self.engine)
        return None

    def create_table(self):
        if self.launch_drop:
            self._drop_table()
        db_meta = ct(self.engine)
        return db_meta.tables

    def _insert_engine(self, table_name, obj, multi=False) -> bool:
        is_committed = False
        with Session(self.engine) as s:
            try:
                if multi:
                    for element in obj:
                        s.add(table_name(**vars(element)))
                else:
                    s.add(table_name(**vars(obj)))
            except sqlalchemy.exc.DataError or sqlalchemy.exc.DatabaseError:
                s.rollback()
            else:
                s.commit()
                is_committed = True
        return is_committed

    def insert(self, inst) -> bool:
        def _exception():
            raise Exception(f'Wrong type accepted - {type(inst)}, expected: Target, Favorite or list of Photo')

        if isinstance(inst, Target):
            return self._insert_engine(TargetTable, inst)
        elif isinstance(inst, Favorite):
            return self._insert_engine(FavoriteTable, inst)
        elif isinstance(inst, list):
            for element in inst:
                if not isinstance(element, Photo):
                    _exception()
            else:
                return self._insert_engine(PhotoTable, inst, multi=True)
        else:
            _exception()

    def add_to_favorite(self, target: Target, favorite: Favorite, photos_list: list) -> bool:
        for inst in (target, favorite, photos_list):
            result = self.insert(inst)
            if not result:
                return False
        return True

    def get_client_favorites_list(self, client_vk_id: int) -> FavoritesList:
        with Session(self.engine) as s:
            statement_1 = sq.select(TargetTable).join(FavoriteTable).filter_by(client_vk_id=client_vk_id)
            favorites_list = FavoritesList(s.scalars(statement_1).all())
            for target in favorites_list.favorites:
                statement_2 = sq.select(PhotoTable).filter_by(target_vk_id=target.vk_id)
                target.photos_list = s.scalars(statement_2).all()
        return favorites_list


# if __name__ == '__main__':
#     def test1():
#         db_test = DatabaseInterface()
#         db_test.create_table()
#
#         sample_targets = [(1, 'Сергей', 'Петров', 'https://serega.mvp'),
#                           (10, 'Екатерина', 'Смирнова', 'https://katuha.yo'),
#                           (101, 'Захар', 'Человеков', 'https://ch.org'),
#                           (102, 'Надежда', 'Прокофьева', 'https://prokoffe.net')
#                           ]
#         [db_test.insert(Target(t[0], t[1], t[2], t[3])) for t in sample_targets]
#
#         sample_photos = [Photo(1, 'https://serega.mvp/1.jpg', 3),
#                          Photo(1, 'https://serega.mvp/2.jpg', 0),
#                          Photo(1, 'https://serega.mvp/3.jpg', 5),
#                          Photo(10, 'https://katuha.yo/1.jpg', 999),
#                          Photo(10, 'https://katuha.yo/2.jpg', 999),
#                          Photo(10, 'https://katuha.yo/3.jpg', 0),
#                          Photo(10, 'https://katuha.yo/4.jpg', 0),
#                          Photo(101, 'https://ivanov.org/1.jpg', 0),
#                          Photo(101, 'https://ivanov.org/2.jpg', 0),
#                          Photo(102, 'https://prokoffe.net/jpg.jpg', 123)]
#
#         db_test.insert(sample_photos)
#
#         sample_favorites = [(901, 1), (901, 102), (903, 101), (902, 10)]
#         [db_test.insert(Favorite(f[0], f[1])) for f in sample_favorites]
#
#         favorites_with_photo = db_test.get_client_favorites_list(client_vk_id=903)
#         for target_ in favorites_with_photo:
#             print(target_.vk_id, target_.name, target_.surname, target_.photos_list)
#     test1()
