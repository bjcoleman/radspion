"""Mission dashboard and detail view models."""

from dataclasses import dataclass, field

from markupsafe import Markup


@dataclass(frozen=True)
class MissionSummary:
    """Mission newly listed after clearance grant or data submit."""

    title: str
    slug: str
    group_name: str


@dataclass(frozen=True)
class MissionListResult:
    """Result of granting clearance or submitting mission data (UC-019 / UC-019b / UC-020)."""

    outcome: str  # success | invalid | already_done
    new_missions: tuple[MissionSummary, ...] = ()
    message: str | None = None

    def to_api_dict(self) -> dict:
        """Serialize for POST /api/clearance and submit responses."""
        data: dict = {"outcome": self.outcome}
        if self.message is not None:
            data["message"] = self.message
        if self.outcome == "success":
            data["new_missions"] = [
                {
                    "title": mission.title,
                    "slug": mission.slug,
                    "group_name": mission.group_name,
                }
                for mission in self.new_missions
            ]
        elif self.outcome == "already_done":
            data["new_missions"] = []
        return data


@dataclass(frozen=True)
class ListedMissionContent:
    """Listed mission prose and status from storage (before HTML render)."""

    slug: str
    title: str
    status: str
    brief_markdown: str
    debrief_markdown: str
    completion_data: str | None = None


@dataclass(frozen=True)
class MissionDetail:
    """Mission detail page (UC-016)."""

    slug: str
    title: str
    status: str
    brief_html: Markup
    debrief_html: Markup
    recovered_data: str | None = None


@dataclass(frozen=True)
class DashboardMission:
    """One mission row on the agent dashboard."""

    slug: str
    title: str
    status: str  # active | completed


@dataclass
class DashboardGroup:
    """Story-arc section on the agent dashboard."""

    id: int
    name: str
    missions: list[DashboardMission] = field(default_factory=list)

    @property
    def active_count(self) -> int:
        return sum(1 for mission in self.missions if mission.status == "active")

    @property
    def completed_count(self) -> int:
        return sum(1 for mission in self.missions if mission.status == "completed")

    def counts_label(self, *, show_completed: bool = True) -> str:
        """Human-readable counts for the group summary (mockup style)."""
        parts: list[str] = []
        if self.active_count:
            parts.append(f"{self.active_count} active")
        if self.completed_count:
            if show_completed:
                parts.append(f"{self.completed_count} completed")
            else:
                parts.append(f"{self.completed_count} completed (hidden)")
        return " · ".join(parts)
