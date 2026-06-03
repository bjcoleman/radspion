"""Application (business) layer for Radspion."""

from radspion.markdown_render import render_mission_markdown
from radspion.missions import (
    DashboardGroup,
    DashboardMission,
    MissionDetail,
    SubmitDataResult,
)
from radspion.oauth_types import GoogleProfile
from radspion.user import User


class Radspion:
    """Business logic; uses a storage implementation for persistence."""

    def __init__(self, storage) -> None:
        self._storage = storage

    def get_user(self, user_id: int) -> User | None:
        """Load a user by primary key."""
        return self._storage.find_user_by_id(user_id)

    def sign_in_with_google(
        self,
        profile: GoogleProfile,
    ) -> User:
        """
        Resolve an existing user or provision a new agent after Google OAuth.

        Existing users are matched by google_subject_id, then email.
        New users are provisioned automatically after verified Google OAuth.
        """
        user = self._storage.find_user_by_google_subject_id(profile.google_subject_id)
        if user is None:
            user = self._storage.find_user_by_email(profile.email)
        if user is not None:
            self.sync_mission_status(user.id)
            return user

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

    def get_mission_detail(self, user_id: int, slug: str) -> MissionDetail | None:
        """Mission detail for a listed mission, or None (UC-016 / UC-017)."""
        content = self._storage.get_listed_mission_content(user_id, slug)
        if content is None:
            return None
        return MissionDetail(
            slug=content.slug,
            title=content.title,
            status=content.status,
            brief_html=render_mission_markdown(content.brief_markdown),
            debrief_html=render_mission_markdown(content.debrief_markdown),
            recovered_code=content.completion_code,
        )

    def submit_data(self, user_id: int, raw_data: str) -> SubmitDataResult:
        """
        Submit field data for the signed-in agent.

        Trims whitespace; comparison is case-sensitive. Resolves unlock codes
        before completion codes.
        """
        data = raw_data.strip()
        if not data:
            return SubmitDataResult(outcome="invalid")
        return self._storage.submit_data(user_id, data)
