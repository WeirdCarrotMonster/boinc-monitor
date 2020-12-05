from dataclasses import dataclass, asdict
from typing import Optional, List
from enum import IntEnum
from datetime import datetime


class ResultState(IntEnum):

    New = 0
    FilesDownloading = 1
    FilesDownloaded = 2
    ComputeError = 3
    FilesUploading = 4
    FilesUploaded = 5
    Aborted = 6
    UploadFailed = 7


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
    platform: str
    project_url: str
    final_cpu_time: float
    final_elapsed_time: float
    estimated_cpu_time_remaining: float
    state: ResultState

    received_time: datetime
    report_deadline: datetime

    active_task: ActiveTask


@dataclass
class SimpleGuiInfo:

    host: HostInfo
    projects: List[ProjectInfo]
    results: List[Result]

    @property
    def asdict(self):
        return asdict(self)
