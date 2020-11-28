from dataclasses import dataclass, asdict
from typing import Optional, List


@dataclass(frozen=True)
class HostInfo:

    name: str


@dataclass
class ProjectInfo:

    project_name: str
    master_url: str
    user_name: str
    team_name: Optional[str] = None


@dataclass
class ActiveTask:

    fraction_done: float
    elapsed_time: float


@dataclass
class Result:

    name: str
    wu_name: str
    project_url: str

    active_task: ActiveTask


@dataclass
class SimpleGuiInfo:

    host: HostInfo
    projects: List[ProjectInfo]
    results: List[Result]

    @property
    def asdict(self):
        return asdict(self)
