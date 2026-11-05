import pytest


def test_list_artworks_empty(client):
    response = client.get("/artworks/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_seeded_artwork(client, seeded_db):
    expected = {"id": 1, **seeded_db[0]}
    response = client.get("/artworks/1")
    assert response.status_code == 200
    assert response.json() == expected


def test_create_artwork(client, sample_artwork):
    response = client.post("/artworks/", json=sample_artwork)
    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["id"], int)
    assert {k: v for k, v in body.items() if k != "id"} == sample_artwork


def test_create_artwork_is_saved(client, created_artwork):
    response = client.get(f"/artworks/{created_artwork['id']}")
    assert response.status_code == 200
    assert response.json() == created_artwork


def test_update_artwork(client, created_artwork, updated_artwork):
    artwork_id = created_artwork["id"]
    expected = {"id": artwork_id, **updated_artwork}

    response = client.put(f"/artworks/{artwork_id}", json=updated_artwork)
    assert response.status_code == 200
    assert response.json() == expected

    # prove it was actually saved, not just echoed back
    assert client.get(f"/artworks/{artwork_id}").json() == expected


def test_delete_artwork(client, created_artwork):
    artwork_id = created_artwork["id"]
    response = client.delete(f"/artworks/{artwork_id}")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/artworks/{artwork_id}").status_code == 404

@pytest.mark.parametrize(
    "method, use_body",
    [("get", False), ("put", True), ("delete", False)],
    ids=["get", "put", "delete"],
)
def test_artwork_not_found(client, sample_artwork, method, use_body):
    kwargs = {"json": sample_artwork} if use_body else {}
    response = client.request(method, "/artworks/9999", **kwargs)
    assert response.status_code == 404
    assert response.json() == {"detail": "Artwork not found"}


def test_non_integer_id(client):
    response = client.get("/artworks/mona-lisa")
    assert response.status_code == 422


DUPLICATE_DETAIL = "An artwork with that title and artist already exists"


def test_create_duplicate(client, created_artwork, sample_artwork):
    response = client.post("/artworks/", json=sample_artwork)
    assert response.status_code == 409
    assert response.json() == {"detail": DUPLICATE_DETAIL}


def test_create_duplicate_ignores_case(client, created_artwork, sample_artwork):
    shouty = {
        **sample_artwork,
        "title": sample_artwork["title"].upper(),
        "artist": sample_artwork["artist"].lower(),
    }
    response = client.post("/artworks/", json=shouty)
    assert response.status_code == 409
    assert response.json() == {"detail": DUPLICATE_DETAIL}

def test_update_into_duplicate(client, seeded_db):
    body = {
        **seeded_db[1],
        "title": seeded_db[0]["title"],
        "artist": seeded_db[0]["artist"],
    }
    response = client.put("/artworks/2", json=body)
    assert response.status_code == 409
    # artwork 2 must be unchanged
    assert client.get("/artworks/2").json() == {"id": 2, **seeded_db[1]}


def test_update_same_title_and_artist_is_allowed(client, created_artwork, sample_artwork):
    body = {**sample_artwork, "museum": "Some Other Museum"}
    response = client.put(f"/artworks/{created_artwork['id']}", json=body)
    assert response.status_code == 200
    assert response.json()["museum"] == "Some Other Museum"

FIELDS = ["title", "artist", "year", "medium", "museum", "image_url"]


@pytest.mark.parametrize("missing_field", FIELDS, ids=FIELDS)
def test_create_missing_field(client, sample_artwork, missing_field):
    body = {k: v for k, v in sample_artwork.items() if k != missing_field}
    response = client.post("/artworks/", json=body)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", missing_field]


@pytest.mark.parametrize(
    "field, bad_value",
    [("year", 3000), ("year", "nineteen-oh-seven"), ("title", "")],
    ids=["future-year", "year-not-int", "empty-title"],
)
def test_create_invalid_value(client, sample_artwork, field, bad_value):
    response = client.post("/artworks/", json={**sample_artwork, field: bad_value})
    assert response.status_code == 422


@pytest.mark.parametrize(
    "params, expected_count",
    [
        ({}, 10),                      # default limit is 10, with 11 seeded
        ({"limit": 3}, 3),
        ({"skip": 10}, 1),             # 11 total, skip 10 -> 1 left
        ({"skip": 5, "limit": 3}, 3),
        ({"limit": 0}, 0),
        ({"skip": 50}, 0),             # past the end of the data
    ],
    ids=["default", "limit-3", "skip-10", "skip-5-limit-3", "limit-0", "skip-past-end"],
)
def test_pagination_counts(client, seeded_db, params, expected_count):
    response = client.get("/artworks/", params=params)
    assert response.status_code == 200
    assert len(response.json()) == expected_count


@pytest.mark.parametrize(
    "params",
    [{"limit": 500}, {"skip": -1}],
    ids=["limit-too-big", "negative-skip"],
)
def test_pagination_invalid(client, seeded_db, params):
    response = client.get("/artworks/", params=params)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "artist, expected_titles",
    [
        (
            "Claude Monet",
            [
                "Impression, Sunrise",
                "Woman with a Parasol – Madame Monet and Her Son",
            ],
        ),
        ("da vinci", ["Mona Lisa", "Lady with an Ermine"]),
        ("Nobody McFake", []),
    ],
    ids=["exact", "lowercase-partial", "no-match"],
)
def test_filter_by_artist(client, seeded_db, artist, expected_titles):
    response = client.get("/artworks/", params={"artist": artist})
    assert response.status_code == 200
    assert [a["title"] for a in response.json()] == expected_titles