from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Main database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./artworks.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Give each request its own database session, and close it afterward.

    Every endpoint asks for this with `Depends(get_db)`. In your tests, you'll
    swap it out for a version that points at a throwaway in-memory database.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
