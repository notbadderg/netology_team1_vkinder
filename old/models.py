import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class TargetTable(Base):
    __tablename__ = "target"
    vk_id = sq.Column(sq.Integer, nullable=False, primary_key=True, autoincrement=False)
    first_name = sq.Column(sq.VARCHAR(length=50), nullable=False)
    last_name = sq.Column(sq.VARCHAR(length=50), nullable=False)
    url = sq.Column(sq.TEXT, nullable=False)
    favorite = relationship("FavoriteTable", back_populates="target")
    photo = relationship("PhotoTable", backref="targets", cascade="all,delete")


class FavoriteTable(Base):
    __tablename__ = "favorite"
    client_vk_id = sq.Column(sq.Integer, nullable=False)
    target_vk_id = sq.Column(sq.Integer, sq.ForeignKey("target.vk_id"), nullable=False)
    target = relationship("TargetTable", back_populates="favorite", single_parent="True", cascade="all,delete")
    c3 = sq.PrimaryKeyConstraint(client_vk_id, target_vk_id)


class PhotoTable(Base):
    __tablename__ = "photo"
    photo_id = sq.Column(sq.TEXT, nullable=False)
    target_vk_id = sq.Column(sq.Integer, sq.ForeignKey("target.vk_id"), nullable=False)
    target = relationship("TargetTable", backref='targets', cascade='all,delete')
    photo_link = sq.Column(sq.TEXT, nullable=False)
    c2 = sq.PrimaryKeyConstraint(photo_id, target_vk_id)


def create_tables(engine, launch_drop, echo):
    if launch_drop:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    # For activating engine echo AFTER creating tables.
    engine.echo = echo
    return Base.metadata


