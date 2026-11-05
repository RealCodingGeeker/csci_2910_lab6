from sqlalchemy import Column, Integer, String

from app.database import Base


class Artwork(Base):
    __tablename__ = "artworks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    artist = Column(String, index=True)
    year = Column(Integer)
    medium = Column(String)
    museum = Column(String)
    image_url = Column(String)
