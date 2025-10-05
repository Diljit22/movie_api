"""
Unit tests for the JSONFileFavorites service.
"""

from movie_api.services.favorites_service import JSONFileFavorites


def test_favorites_add_and_check(tmp_path):
    """Tests adding a favorite and checking its existence."""
    favorites_file = tmp_path / "favorites.json"
    favorites_service = JSONFileFavorites(filepath=str(favorites_file))

    assert not favorites_service.is_favorite(550)

    favorites_service.add(550)

    assert favorites_service.is_favorite(550)
    assert favorites_service.get_all() == [550]


def test_favorites_remove(tmp_path):
    """Tests removing a favorite."""
    favorites_file = tmp_path / "favorites.json"
    favorites_service = JSONFileFavorites(filepath=str(favorites_file))

    favorites_service.add(550)
    favorites_service.add(123)

    assert favorites_service.is_favorite(550)

    favorites_service.remove(550)

    assert not favorites_service.is_favorite(550)
    assert favorites_service.get_all() == [123]


def test_favorites_add_duplicate(tmp_path):
    """Tests that adding a duplicate favorite does not change the list."""
    favorites_file = tmp_path / "favorites.json"
    favorites_service = JSONFileFavorites(filepath=str(favorites_file))

    favorites_service.add(550)
    favorites_service.add(550)

    assert favorites_service.get_all() == [550]
