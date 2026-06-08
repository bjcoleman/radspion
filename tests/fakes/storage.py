"""In-memory storage fakes for tests."""

from radspion.activity import FieldActivity
from radspion.codename import DUPLICATE_CODENAME_MESSAGE, SUCCESS_MESSAGE, CodenameUpdateResult
from radspion.missions import DashboardGroup, DashboardMission
from radspion.personnel import PersonnelFile
from radspion.user import User


class InMemoryRadspionStorage:
    """In-memory users for auth-focused tests."""

    def __init__(
        self,
        users: list[User] | None = None,
    ) -> None:
        self._users: dict[int, User] = {}
        self._next_user_id = 1
        self._next_codename_sequence = 0
        for user in users or ():
            self._users[user.id] = user
            self._next_user_id = max(self._next_user_id, user.id + 1)

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

    def find_user_by_codename(self, codename: str) -> User | None:
        for user in self._users.values():
            if user.codename == codename:
                return user
        return None

    def _create_codename(self) -> str:
        self._next_codename_sequence += 1
        return f"AGENT{self._next_codename_sequence:04d}"

    def create_user(
        self,
        *,
        email: str,
        google_subject_id: str,
        display_name: str,
        is_operator: bool = False,
    ) -> User:
        codename = self._create_codename()
        user_id = self._next_user_id
        self._next_user_id += 1
        user = User(
            id=user_id,
            email=email,
            google_subject_id=google_subject_id,
            display_name=display_name,
            codename=codename,
            is_operator=is_operator,
        )
        self._users[user_id] = user
        return user

    def update_user_codename(self, user_id: int, codename: str) -> CodenameUpdateResult:
        user = self._users.get(user_id)
        if user is None:
            return CodenameUpdateResult(outcome="invalid", message=DUPLICATE_CODENAME_MESSAGE)
        for other in self._users.values():
            if other.id != user_id and other.codename == codename:
                return CodenameUpdateResult(
                    outcome="invalid",
                    message=DUPLICATE_CODENAME_MESSAGE,
                )
        updated = User(
            id=user.id,
            email=user.email,
            google_subject_id=user.google_subject_id,
            display_name=user.display_name,
            codename=codename,
            is_operator=user.is_operator,
        )
        self._users[user_id] = updated
        return CodenameUpdateResult(outcome="success", message=SUCCESS_MESSAGE)

    def sync_mission_status(self, user_id: int) -> None:
        """No-op — mission tests use SQLite fixtures."""
        _ = user_id

    def get_agent_dashboard(self, user_id: int) -> list[DashboardGroup]:
        _ = user_id
        return []

    def find_listed_mission(self, user_id: int, slug: str) -> DashboardMission | None:
        _ = user_id
        _ = slug
        return None

    def get_personnel_file(self, user_id: int) -> PersonnelFile | None:
        _ = user_id
        return None

    def get_field_activity(self) -> FieldActivity:
        return FieldActivity(
            top_agents=(),
            storylines=(),
            recent_clearances=(),
            recent_completions=(),
        )
