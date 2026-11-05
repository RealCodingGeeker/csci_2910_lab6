from sqlalchemy.orm import Session

from app.database import engine
from app.models import Artwork, Base

# Real works, checked against Wikidata and Wikipedia. Images are from Wikimedia Commons
# (via each work's Wikipedia article). For works made over several years, `year` is the
# year the artist started.
artworks_data = [
    {
        "title": "Mona Lisa",
        "artist": "Leonardo da Vinci",
        "year": 1503,
        "medium": "Oil on poplar panel",
        "museum": "Louvre",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg",
    },
    {
        "title": "Lady with an Ermine",
        "artist": "Leonardo da Vinci",
        "year": 1489,
        "medium": "Oil on walnut panel",
        "museum": "Czartoryski Museum",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/bf/Lady_with_an_Ermine_-_Leonardo_da_Vinci_%28adjusted_levels%29.jpg",
    },
    {
        "title": "Impression, Sunrise",
        "artist": "Claude Monet",
        "year": 1872,
        "medium": "Oil on canvas",
        "museum": "Musée Marmottan Monet",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/59/Monet_-_Impression%2C_Sunrise.jpg",
    },
    {
        "title": "Woman with a Parasol – Madame Monet and Her Son",
        "artist": "Claude Monet",
        "year": 1875,
        "medium": "Oil on canvas",
        "museum": "National Gallery of Art",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/1b/Claude_Monet_-_Woman_with_a_Parasol_-_Madame_Monet_and_Her_Son_-_Google_Art_Project.jpg",
    },
    {
        "title": "The Starry Night",
        "artist": "Vincent van Gogh",
        "year": 1889,
        "medium": "Oil on canvas",
        "museum": "Museum of Modern Art",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
    },
    {
        "title": "Girl with a Pearl Earring",
        "artist": "Johannes Vermeer",
        "year": 1665,
        "medium": "Oil on canvas",
        "museum": "Mauritshuis",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0f/1665_Girl_with_a_Pearl_Earring.jpg",
    },
    {
        "title": "The Night Watch",
        "artist": "Rembrandt",
        "year": 1642,
        "medium": "Oil on canvas",
        "museum": "Rijksmuseum",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/3a/La_ronda_de_noche%2C_por_Rembrandt_van_Rijn.jpg",
    },
    {
        "title": "A Sunday Afternoon on the Island of La Grande Jatte",
        "artist": "Georges Seurat",
        "year": 1884,
        "medium": "Oil on canvas",
        "museum": "Art Institute of Chicago",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/7d/A_Sunday_on_La_Grande_Jatte%2C_Georges_Seurat%2C_1884.jpg",
    },
    {
        "title": "American Gothic",
        "artist": "Grant Wood",
        "year": 1930,
        "medium": "Oil on beaverboard",
        "museum": "Art Institute of Chicago",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Grant_Wood_-_American_Gothic_%281930%29.jpg",
    },
    {
        "title": "Las Meninas",
        "artist": "Diego Velázquez",
        "year": 1656,
        "medium": "Oil on canvas",
        "museum": "Museo del Prado",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/31/Las_Meninas%2C_by_Diego_Vel%C3%A1zquez%2C_from_Prado_in_Google_Earth.jpg",
    },
    {
        "title": "Bal du moulin de la Galette",
        "artist": "Pierre-Auguste Renoir",
        "year": 1876,
        "medium": "Oil on canvas",
        "museum": "Musée d'Orsay",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Renoir%2C_Pierre-Auguste_-_Dance_at_Le_Moulin_de_la_Galette%2C_1876.jpg",
    },
]


def populate():
    """Create the table and seed it, but only if it's empty (so your changes survive a restart)."""
    Base.metadata.create_all(bind=engine)
    with Session(bind=engine) as session:
        if session.query(Artwork).count() > 0:
            return
        for artwork in artworks_data:
            session.add(Artwork(**artwork))
        session.commit()


def reset():
    """Wipe the table and re-seed it. Run with `python -m app.scripts.populate_db`"""
    Base.metadata.create_all(bind=engine)
    with Session(bind=engine) as session:
        session.query(Artwork).delete()
        session.commit()
    populate()


if __name__ == "__main__":
    reset()
