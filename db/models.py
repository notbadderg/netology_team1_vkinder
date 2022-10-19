import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class TargetTable(Base):
    __tablename__ = "target"
    vk_id = sq.Column(sq.Integer, nullable=False, primary_key=True, autoincrement=False)
    name = sq.Column(sq.VARCHAR(length=50), nullable=False)
    surname = sq.Column(sq.VARCHAR(length=50), nullable=False)
    url = sq.Column(sq.TEXT, nullable=False)


class FavoriteTable(Base):
    __tablename__ = "favorite"
    client_vk_id = sq.Column(sq.Integer, nullable=False)
    target_vk_id = sq.Column(sq.Integer, sq.ForeignKey("target.vk_id"), nullable=False)
    target = relationship(TargetTable, backref="favorites")
    c3 = sq.PrimaryKeyConstraint(client_vk_id, target_vk_id)


class PhotoTable(Base):
    __tablename__ = "photo"
    target_vk_id = sq.Column(sq.Integer, sq.ForeignKey("target.vk_id"), nullable=False)
    target = relationship(TargetTable, backref="photos")
    url = sq.Column(sq.TEXT, nullable=False)
    likes = sq.Column(sq.Integer, nullable=False)
    c1 = sq.CheckConstraint(likes >= 0)
    c2 = sq.PrimaryKeyConstraint(target_vk_id, url)


def drop_tables(engine):
    Base.metadata.drop_all(engine)
    return None


def create_tables(engine):
    Base.metadata.create_all(engine)
    return Base.metadata


