"""Application (business) layer for Radspion."""

from radspion.activity import FieldActivity
from radspion.codename import (
    DUPLICATE_CODENAME_MESSAGE,
    INVALID_LENGTH_MESSAGE,
    SUCCESS_MESSAGE,
    CodenameUpdateResult,
    codename_length_valid,
)
from radspion.markdown_render import render_mission_markdown
from radspion.missions import DashboardGroup, DashboardMission, MissionDetail, MissionListResult
from radspion.oauth_types import GoogleProfile
from radspion.personnel import PersonnelFile
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

    def get_personnel_file(self, user_id: int) -> PersonnelFile | None:
        """Load Agent Personnel File data for the signed-in agent."""
        return self._storage.get_personnel_file(user_id)

    def get_field_activity(self) -> FieldActivity:
        """Load public Field Activity aggregates."""
        return self._storage.get_field_activity()

    def update_codename(self, user_id: int, raw_codename: str) -> CodenameUpdateResult:
        """
        Update the signed-in agent's codename.

        Trims outer whitespace. Comparison for uniqueness is case-sensitive exact match.
        """
        codename = raw_codename.strip()
        if not codename_length_valid(codename):
            return CodenameUpdateResult(outcome="invalid", message=INVALID_LENGTH_MESSAGE)

        user = self._storage.find_user_by_id(user_id)
        if user is None:
            return CodenameUpdateResult(outcome="invalid", message=INVALID_LENGTH_MESSAGE)

        if user.codename == codename:
            return CodenameUpdateResult(outcome="success", message=SUCCESS_MESSAGE)

        existing = self._storage.find_user_by_codename(codename)
        if existing is not None and existing.id != user_id:
            return CodenameUpdateResult(outcome="invalid", message=DUPLICATE_CODENAME_MESSAGE)

        return self._storage.update_user_codename(user_id, codename)

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
            recovered_data=content.completion_data,
        )

    def grant_clearance(self, user_id: int, raw_code: str) -> MissionListResult:
        """
        Grant clearance for the signed-in agent.

        Trims whitespace; comparison is case-sensitive.
        """
        code = raw_code.strip()
        if not code:
            return MissionListResult(outcome="invalid")
        return self._storage.grant_clearance(user_id, code)

    def submit_mission_data(
        self,
        user_id: int,
        slug: str,
        raw_data: str,
    ) -> MissionListResult | None:
        """
        Submit recovered mission data for the signed-in agent.

        Trims whitespace; comparison is case-sensitive.
        Returns None when the mission is not on the agent's list.
        """
        data = raw_data.strip()
        if not data:
            return MissionListResult(outcome="invalid")
        return self._storage.submit_mission_data(user_id, slug, data)
