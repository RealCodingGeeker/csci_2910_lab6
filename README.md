# art_api

A REST API for famous works of art, built with FastAPI and SQLAlchemy. Unlike the Cryptid API from Lab 5, this one is **already finished**: every endpoint works. Your job in Lab 6 is to prove it with automated tests written in **pytest**.

## What's in here

```
lab6_starter/
├── app/
│   ├── main.py              # App setup, middleware, router registration
│   ├── database.py          # Database engine, session, and the get_db dependency
│   ├── models.py            # SQLAlchemy ORM model (maps to the artworks table)
│   ├── schemas.py           # Pydantic schemas (shapes and rules for request/response data)
│   ├── routers/
│   │   └── artworks.py      # Route handlers for all /artworks endpoints
│   └── scripts/
│       └── populate_db.py   # Seeds the database with 11 real artworks
├── tests/                   # Empty. Your tests go here.
│   └── __init__.py
├── artworks.db              # SQLite database, pre-seeded
├── requirements.txt         # Dependencies, including pytest (for pip)
└── pyproject.toml           # Project metadata (for uv) and pytest settings
```

## The data

The database is seeded with 11 real paintings, checked against Wikidata and Wikipedia. Image URLs point to Wikimedia Commons.

<div align="center">

| ID | Title | Artist | Year | Museum |
|---|---|---|---|---|
| 1 | Mona Lisa | Leonardo da Vinci | 1503 | Louvre |
| 2 | Lady with an Ermine | Leonardo da Vinci | 1489 | Czartoryski Museum |
| 3 | Impression, Sunrise | Claude Monet | 1872 | Musée Marmottan Monet |
| 4 | Woman with a Parasol – Madame Monet and Her Son | Claude Monet | 1875 | National Gallery of Art |
| 5 | The Starry Night | Vincent van Gogh | 1889 | Museum of Modern Art |
| 6 | Girl with a Pearl Earring | Johannes Vermeer | 1665 | Mauritshuis |
| 7 | The Night Watch | Rembrandt | 1642 | Rijksmuseum |
| 8 | A Sunday Afternoon on the Island of La Grande Jatte | Georges Seurat | 1884 | Art Institute of Chicago |
| 9 | American Gothic | Grant Wood | 1930 | Art Institute of Chicago |
| 10 | Las Meninas | Diego Velázquez | 1656 | Museo del Prado |
| 11 | Bal du moulin de la Galette | Pierre-Auguste Renoir | 1876 | Musée d'Orsay |

</div>

For works painted over several years (the Mona Lisa, La Grande Jatte), `year` is the year the artist started.

## Endpoints

All endpoints are under the `/artworks` prefix.

<div align="center">

| Method | URL | Success | Can also return |
|---|---|---|---|
| `GET` | `/artworks/` | `200` | `422` (bad `skip` / `limit`) |
| `GET` | `/artworks/{id}` | `200` | `404`, `422` |
| `POST` | `/artworks/` | `201` | `409`, `422` |
| `PUT` | `/artworks/{id}` | `200` | `404`, `409`, `422` |
| `DELETE` | `/artworks/{id}` | `204` | `404`, `422` |

</div>

`GET /artworks/` takes three optional query parameters:

- `skip` (default `0`, can't be negative)
- `limit` (default `10`, must be between `0` and `100`)
- `artist`, which keeps only works whose artist *contains* that text, ignoring case (`?artist=monet`)

Results are always ordered by ID.

## Rules the API enforces

- Every field (`title`, `artist`, `year`, `medium`, `museum`, `image_url`) is required on `POST` and `PUT`.
- `title` and `artist` can't be empty strings.
- `year` must be a whole number and can't be in the future.
- Two artworks can't have the same title **and** artist. The check ignores case, so `"MONA LISA"` by `"leonardo da vinci"` counts as a duplicate. Breaking this rule returns `409 Conflict`.

## Getting started

### Prerequisites

- Python 3.10+

### Setup

From inside the project folder, create a virtual environment and install the dependencies:

**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

To run the server:

```bash
python -m uvicorn app.main:app --reload
```

Then visit `http://localhost:8000/docs`.

To run the tests (you don't need the server running):

```bash
pytest
```

To wipe the database back to the original 11 artworks:

```bash
python -m app.scripts.populate_db
```

If you use uv instead: `uv sync`, then `uv run dev` for the server and `uv run pytest` for the tests.
