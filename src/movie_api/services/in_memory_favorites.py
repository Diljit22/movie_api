"""
Showcase: Open/Closed and Liskov Substitution Principles
impl new service w/o touching routers.
"""

from movie_api.interfaces import FavoritesInterface

class InMemoryFavorites(FavoritesInterface):
    """
    Stores fav movie ID in memory; lost on restart.
    """
    def __init__(self):
        self._fav = []
        
    def add(self, movie_id):
        if movie_id not in self._fav:
            self._fav.append(movie_id)
        
    def remove(self, movie_id):
        if movie_id in self._fav:
            self._fav.remove(movie_id)
    
    def get_all(self):
        return self._fav.copy()
    
    def is_favorite(self, movie_id):
        return movie_id in self._fav