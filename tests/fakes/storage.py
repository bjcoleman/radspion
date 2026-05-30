"""In-memory storage fakes for tests."""

from radspion.user import User

ORIENTATION_GROUP_ID = 1
ORIENTATION_GROUP_NAME = "Orientation"


class InMemoryRadspionStorage:
    """In-memory users, groups, and registration codes."""

    def __init__(
        self,
        registration_codes: set[str] | None = None,
        users: list[User] | None = None,
    ) -> None:
        self._registration_codes = set(registration_codes or ())
        self._users: dict[int, User] = {}
        self._next_user_id = 1
        self._group_members: set[tuple[int, int]] = set()
        for user in users or ():
            self._users[user.id] = user
            self._next_user_id = max(self._next_user_id, user.id + 1)

    def registration_code_exists(self, code: str) -> bool:
        return code in self._registration_codes

    def find_user_by_google_subject_id(self, google_subject_id: str) -> User | None:
        for user in self._users.values():
            if user.google_subject_id == google_subject_id:
                return user
        return None

    def find_user_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def find_user_by_id(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    def create_user(
        self,
        *,
        email: str,
        google_subject_id: str,
        display_name: str,
        is_operator: bool = False,
    ) -> User:
        user_id = self._next_user_id
        self._next_user_id += 1
        user = User(
            id=user_id,
            email=email,
            google_subject_id=google_subject_id,
            display_name=display_name,
            is_operator=is_operator,
        )
        self._users[user_id] = user
        return user

    def get_orientation_group_id(self) -> int | None:
        return ORIENTATION_GROUP_ID

    def add_group_member(self, user_id: int, group_id: int) -> None:
        self._group_members.add((user_id, group_id))

    def user_in_group(self, user_id: int, group_id: int) -> bool:
        return (user_id, group_id) in self._group_members
