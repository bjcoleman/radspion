"""Mission dashboard view models."""

from dataclasses import dataclass, field


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
