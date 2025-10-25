"""In-memory user service for demonstration and testing."""
from datetime import datetime, UTC

from ..interfaces import UserServiceInterface
from ..schemas import User, UserCreate

# Simple in-memory "database"
_users: dict[int, User] = {}
_next_user_id = 1

class InMemoryUserService(UserServiceInterface):
    """Stores user data in a dictionary. Lost on restart."""

    def get_user_by_id(self, user_id: int) -> User | None:
        return _users.get(user_id)

    def get_user_by_email(self, email: str) -> User | None:
        for user in _users.values():
            if user.email == email:
                return user
        return None

    def create_user(self, user_data: UserCreate) -> User:
        """
        Creates a new user.
        
        NOTE: In a real application, you would hash the password here before storing it.
        """
        global _next_user_id
        new_user = User(
            id=_next_user_id,
            created_at=datetime.now(UTC),
            **user_data.model_dump(exclude={"password"}), # Never store plain passwords
        )
        _users[_next_user_id] = new_user
        _next_user_id += 1
        return new_user