"""Application (business) layer for Radspion."""

from radspion.missions import DashboardGroup, DashboardMission
from radspion.oauth_types import GoogleProfile, SignupNotAllowedError
from radspion.user import User


class Radspion:
    """Business logic; uses a storage implementation for persistence."""

    def __init__(self, storage) -> None:
        self._storage = storage

    def validate_registration_code(self, raw_code: str) -> bool:
        """
        Validate a registration access code.

        Trims whitespace; comparison is case-sensitive.
        """
        code = raw_code.strip()
        if not code:
            return False
        return self._storage.registration_code_exists(code)

    def get_user(self, user_id: int) -> User | None:
        """Load a user by primary key."""
        return self._storage.find_user_by_id(user_id)

    def sign_in_with_google(
        self,
        profile: GoogleProfile,
        *,
        registration_cleared: bool,
    ) -> User:
        """
        Resolve an existing user or provision a new agent after Google OAuth.

        Existing users are matched by google_subject_id, then email.
        New users require registration_cleared.
        """
        user = self._storage.find_user_by_google_subject_id(profile.google_subject_id)
        if user is None:
            user = self._storage.find_user_by_email(profile.email)
        if user is not None:
            self.sync_mission_status(user.id)
            return user

        if not registration_cleared:
            raise SignupNotAllowedError()

        user = self._storage.create_user(
            email=profile.email,
            google_subject_id=profile.google_subject_id,
            display_name=profile.display_name,
        )
        self.sync_mission_status(user.id)
        return user

    def sync_mission_status(self, user_id: int) -> None:
        """Keep agent_mission_status in sync for listable missions (UC-012)."""
        self._storage.sync_mission_status(user_id)

    def get_agent_dashboard(self, user_id: int) -> list[DashboardGroup]:
        """Listed missions grouped by story arc for the dashboard."""
        return self._storage.get_agent_dashboard(user_id)

    def find_listed_mission(self, user_id: int, slug: str) -> DashboardMission | None:
        """One mission on the agent's list, or None."""
        return self._storage.find_listed_mission(user_id, slug)
