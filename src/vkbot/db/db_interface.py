import sqlalchemy as sq
import sqlalchemy.exc
from sqlalchemy.orm import Session
from .models import create_tables as ct, FavoriteTable, TargetTable, PhotoTable
from .data_classes import Target, Photo


class DatabaseInterface:
    def __init__(self, db_cfg):
        self.host = db_cfg.host
        self.port = db_cfg.port
        self.password = db_cfg.password
        self.user = db_cfg.user
        self.name = db_cfg.name
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

    def add_to_favorite(self, target, client_vk_id: int) -> bool:
        is_committed = False
        with Session(self.engine) as s:
            try:
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
            except sqlalchemy.exc.DataError or sqlalchemy.exc.DatabaseError:
                s.rollback()
            else:
                try:
                    s.commit()
                except sqlalchemy.exc.IntegrityError:
                    s.rollback()
                else:
                    is_committed = True
        return is_committed

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
                    print(type(photo))
                    temp_target.photos.append(Photo(photo_id=photo.photo_id,
                                                    target_vk_id=photo.target_vk_id,
                                                    photo_link=photo.photo_link))
                favorites_list.append(temp_target)
        return favorites_list
