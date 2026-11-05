from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Artwork
from app.schemas import ArtworkCreate, ArtworkResponse, ArtworkUpdate

router = APIRouter(prefix="/artworks", tags=["artworks"])

NOT_FOUND_DETAIL = "Artwork not found"
CONFLICT_DETAIL = "An artwork with that title and artist already exists"

# These only add the errors to the /docs page. They don't raise anything.
NOT_FOUND: dict[int | str, dict[str, Any]] = {404: {"description": NOT_FOUND_DETAIL}}
CONFLICT: dict[int | str, dict[str, Any]] = {409: {"description": CONFLICT_DETAIL}}


def get_artwork_or_404(artwork_id: int, db: Session) -> Artwork:
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if artwork is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_DETAIL
        )
    return artwork


def check_for_duplicate(
    title: str, artist: str, db: Session, ignore_id: int | None = None
) -> None:
    """Raise a 409 if another artwork already has this title and artist (ignoring case)."""
    query = db.query(Artwork).filter(
        func.lower(Artwork.title) == title.lower(),
        func.lower(Artwork.artist) == artist.lower(),
    )
    if ignore_id is not None:
        query = query.filter(Artwork.id != ignore_id)
    if query.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=CONFLICT_DETAIL
        )


@router.get("/", response_model=list[ArtworkResponse])
def read_artworks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        10, ge=0, le=100, description="Maximum number of records to return (0-100)"
    ),
    artist: str | None = Query(
        None,
        description="Only return works whose artist contains this text (not case-sensitive)",
    ),
    db: Session = Depends(get_db),
):
    """
    Return a list of artworks, ordered by ID.

    - **skip**: number of records to skip (for pagination)
    - **limit**: maximum number of records to return (default 10, max 100)
    - **artist**: optional filter, e.g. `?artist=monet`
    """
    query = db.query(Artwork)
    if artist:
        query = query.filter(Artwork.artist.ilike(f"%{artist}%"))
    return query.order_by(Artwork.id).offset(skip).limit(limit).all()


@router.get("/{artwork_id}", response_model=ArtworkResponse, responses=NOT_FOUND)
def read_artwork(artwork_id: int, db: Session = Depends(get_db)):
    """Return one artwork by its ID. Returns 404 if no artwork has that ID."""
    return get_artwork_or_404(artwork_id, db)


@router.post(
    "/",
    response_model=ArtworkResponse,
    status_code=status.HTTP_201_CREATED,
    responses=CONFLICT,
)
def create_artwork(artwork: ArtworkCreate, db: Session = Depends(get_db)):
    """
    Create a new artwork and return it with its new ID.

    Returns 409 if an artwork with the same title and artist already exists
    (not case-sensitive).
    """
    check_for_duplicate(artwork.title, artwork.artist, db)
    db_artwork = Artwork(**artwork.model_dump())
    db.add(db_artwork)
    db.commit()
    db.refresh(db_artwork)
    return db_artwork


@router.put(
    "/{artwork_id}", response_model=ArtworkResponse, responses={**NOT_FOUND, **CONFLICT}
)
def update_artwork(
    artwork_id: int, artwork: ArtworkUpdate, db: Session = Depends(get_db)
):
    """
    Replace every field of an existing artwork.

    Returns 404 if no artwork has that ID, and 409 if the new title and artist
    match a *different* artwork.
    """
    db_artwork = get_artwork_or_404(artwork_id, db)
    check_for_duplicate(artwork.title, artwork.artist, db, ignore_id=artwork_id)
    for field, value in artwork.model_dump().items():
        setattr(db_artwork, field, value)
    db.commit()
    db.refresh(db_artwork)
    return db_artwork


@router.delete(
    "/{artwork_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND
)
def delete_artwork(artwork_id: int, db: Session = Depends(get_db)):
    """Delete an artwork. Returns 204 with no body, or 404 if no artwork has that ID."""
    db_artwork = get_artwork_or_404(artwork_id, db)
    db.delete(db_artwork)
    db.commit()


