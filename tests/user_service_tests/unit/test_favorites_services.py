import pytest

from user_service.src.user_api.services.favorites_service_json import (
    JSONFileFavoritesService,
)
from user_service.src.user_api.services.in_memory_favorites import (
    InMemoryFavoritesService,
)


# Use parametrize to run the same tests on both service implementations
@pytest.mark.parametrize(
    "service_class", [InMemoryFavoritesService, JSONFileFavoritesService]
)
def test_favorites_services_flow(service_class, tmp_path):
    """
    Tests the full add -> check -> get -> remove -> check flow for favorites services.
    """
    # For the JSON service, we need to provide a temporary file path
    if service_class is JSONFileFavoritesService:
        service = service_class(filepath=str(tmp_path / "favorites.json"))
    else:
        service = service_class()

    user_id = 1
    movie_id_1 = 101
    movie_id_2 = 202

    # Initially, user has no favorites
    assert service.get_all_for_user(user_id) == []
    assert service.is_favorite(user_id, movie_id_1) is False

    # Add a favorite
    service.add(user_id, movie_id_1)
    assert service.is_favorite(user_id, movie_id_1) is True
    assert service.get_all_for_user(user_id) == [movie_id_1]

    # Add another favorite
    service.add(user_id, movie_id_2)
    assert service.is_favorite(user_id, movie_id_2) is True
    # Order might not be guaranteed, so check with a set
    assert set(service.get_all_for_user(user_id)) == {movie_id_1, movie_id_2}

    # Remove the first favorite
    service.remove(user_id, movie_id_1)
    assert service.is_favorite(user_id, movie_id_1) is False
    assert service.get_all_for_user(user_id) == [movie_id_2]

    # Check another user
    assert service.get_all_for_user(user_id=2) == []
