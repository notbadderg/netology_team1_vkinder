import sqlalchemy as sq
import sqlalchemy.exc
from sqlalchemy.orm import Session
# from .models import create_tables as ct, FavoriteTable, TargetTable, PhotoTable
from old.models import create_tables as ct, FavoriteTable, TargetTable, PhotoTable

# from .data_classes import Target, Photo
from src.vkbot.db.data_classes import Target, Photo


class DatabaseInterface:
    def __init__(self, db_cfg):
        self.host = db_cfg.host
        self.port = db_cfg.port
        self.password = db_cfg.password
        self.user = db_cfg.user
        self.name = db_cfg.dbname
        self.launch_drop = db_cfg.launch_drop
        self.echo_creating = db_cfg.echo_creating
        self.echo_queries = db_cfg.echo_queries
        self.engine = sq.create_engine(self._make_dsn(), echo=self.echo_creating)
        self.create_table()

    def _make_dsn(self) -> str:
        driver = "postgresql://"
        credentials = f"{self.user}:{self.password}"
        address = f"{self.host}:{self.port}"
        db_name = self.name
        return f"{driver}{credentials}@{address}/{db_name}"

    def create_table(self):
        db_meta = ct(self.engine, self.launch_drop, self.echo_queries)
        return db_meta.tables

    def add_to_favorite(self, target: Target, client_vk_id: int) -> bool:
        is_committed = False
        with Session(self.engine) as s:
            try:
                s.add(FavoriteTable(client_vk_id=client_vk_id,
                                    target_vk_id=target.vk_id))
                s.commit()
            except sqlalchemy.exc.IntegrityError:
                s.rollback()
                s.add(TargetTable(vk_id=target.vk_id,
                                  first_name=target.first_name,
                                  last_name=target.last_name,
                                  url=target.url))
                s.add(FavoriteTable(client_vk_id=client_vk_id,
                                    target_vk_id=target.vk_id))
                for photo in target.photos:
                    s.add(PhotoTable(photo_id=photo.photo_id,
                                     target_vk_id=photo.target_vk_id,
                                     photo_link=photo.photo_link))
                try:
                    s.commit()
                except sqlalchemy.exc.IntegrityError:
                    s.rollback()
                else:
                    is_committed = True
            else:
                is_committed = True
            return is_committed

    def remove_favorite(self, target: Target, client_vk_id: int) -> bool:
        is_committed = False
        with Session(self.engine) as s:
            statement_del = sq.delete(FavoriteTable).where(FavoriteTable.client_vk_id == client_vk_id,
                                                           FavoriteTable.target_vk_id == target.vk_id)
            s.execute(statement_del)
            try:
                s.commit()
            except sqlalchemy.exc.IntegrityError:
                s.rollback()
            else:
                count_of_targets = s.query(FavoriteTable).where(FavoriteTable.target_vk_id == target.vk_id).count()
                if count_of_targets == 0:
                    statement_del = sq.delete(TargetTable).where(TargetTable.vk_id == target.vk_id)
                    s.execute(statement_del)
                try:
                    s.commit()
                except sqlalchemy.exc.IntegrityError:
                    s.rollback()
                else:
                    is_committed = True
        return is_committed

        #     except sqlalchemy.exc.DataError or sqlalchemy.exc.DatabaseError:
        #         s.rollback()
        #     else:
        #         try:
        #             s.commit()
        #         except sqlalchemy.exc.IntegrityError:
        #             s.rollback()
        #         else:
        #             is_committed = True
        # return is_committed

    def get_client_favorites_list(self, client_vk_id: int) -> list:
        with Session(self.engine) as s:
            statement_1 = sq.select(TargetTable).join(FavoriteTable).filter_by(client_vk_id=client_vk_id)
            rows = s.scalars(statement_1).all()
            favorites_list = []
            for row in rows:
                temp_target = Target(row.vk_id, row.first_name, row.last_name, row.url)
                statement_2 = sq.select(PhotoTable).filter_by(target_vk_id=temp_target.vk_id)
                temp_photos_list = s.scalars(statement_2).all()
                for photo in temp_photos_list:
                    temp_target.photos.append(Photo(photo_id=photo.photo_id,
                                                    target_vk_id=photo.target_vk_id,
                                                    photo_link=photo.photo_link))
                favorites_list.append(temp_target)
        return favorites_list


if __name__ == '__main__':

    from src.config import DatabaseConfig

    db_cfg1 = DatabaseConfig()
    dbi = DatabaseInterface(db_cfg1)
    client_1 = 1
    client_2 = 100
    target_1 = Target(vk_id=2100000111, first_name='Test1', last_name='Test1', url='sample_url')
    target_2 = Target(vk_id=2100000999, first_name='Test2', last_name='Test2', url='sample_url')
    target_1_photos = [Photo(**{'photo_id': 2100000111, 'target_vk_id': 2100000111, 'photo_link': '123'}),
                       Photo(**{'photo_id': 2100000112, 'target_vk_id': 2100000111, 'photo_link': '123'})]
    target_2_photos = [Photo(**{'photo_id': 2100000113, 'target_vk_id': 2100000999, 'photo_link': '123'}),
                       Photo(**{'photo_id': 2100000114, 'target_vk_id': 2100000999, 'photo_link': '123'})]


    target_1.photos = target_1_photos
    target_2.photos = target_2_photos

    print(dbi.add_to_favorite(target_1, client_1))
    print(dbi.add_to_favorite(target_1, client_2))
    print(dbi.get_client_favorites_list(client_1))
    # print(dbi.remove_favorite(target_1, client_1))
    # print(dbi.remove_favorite(target_1, client_2))
    pass