import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Artwork
from app.scripts.populate_db import artworks_data

# A throwaway database that lives in memory (RAM) and disappears when the tests finish.
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def get_test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client():
    """A fake browser that sends requests straight to the app, using the test database."""
    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_db():
    """Runs before EVERY test: start each one with empty tables."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield


@pytest.fixture
def seeded_db():
    """Fill the test database with the same 11 artworks the real one starts with."""
    with TestingSessionLocal() as db:
        db.add_all(Artwork(**artwork) for artwork in artworks_data)
        db.commit()
    return artworks_data


# Three more Fixtures
@pytest.fixture
def sample_artwork():
    return {
        "title": "The Kiss",
        "artist": "Gustav Klimt",
        "year": 1907,
        "medium": "Oil and gold leaf on canvas",
        "museum": "Belvedere",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/40/The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg",
    }


@pytest.fixture
def updated_artwork():
    return {
        "title": "The Scream",
        "artist": "Edvard Munch",
        "year": 1893,
        "medium": "Oil, tempera and pastel on cardboard",
        "museum": "National Museum of Norway",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c5/Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg",
    }


@pytest.fixture
def created_artwork(client, sample_artwork):
    response = client.post("/artworks/", json=sample_artwork)
    assert response.status_code == 201
    return response.json()