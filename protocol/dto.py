from datetime import datetime
from enum import IntEnum
from typing import Optional

from pydantic import BaseModel


class ResultState(IntEnum):

    New = 0
    FilesDownloading = 1
    FilesDownloaded = 2
    ComputeError = 3
    FilesUploading = 4
    FilesUploaded = 5
    Aborted = 6
    UploadFailed = 7


class ActiveTaskState(IntEnum):

    Uninitialized = 0
    Executing = 1
    AbortPending = 5
    QuitPending = 8
    Suspended = 9
    CopyPending = 10


class HostInfo(BaseModel):

    name: str

    class Config:
        allow_mutation = False
        extra = "ignore"

    @property
    def asdict(self):
        return {"name": self.name}


class ProjectInfo(BaseModel):

    project_name: str
    master_url: str
    user_name: str
    team_name: Optional[str] = None

    class Config:
        extra = "ignore"

    @property
    def asdict(self):
        return {
            "project_name": self.project_name,
            "master_url": self.master_url,
            "user_name": self.user_name,
            "team_name": self.team_name,
        }


class ActiveTask(BaseModel):

    active_task_state: ActiveTaskState
    fraction_done: float
    elapsed_time: float

    class Config:
        extra = "ignore"

    @property
    def asdict(self):
        return {
            "active_task_state": self.active_task_state.name,
            "fraction_done": self.fraction_done,
            "elapsed_time": self.elapsed_time,
        }


class Result(BaseModel):

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

    class Config:
        extra = "ignore"

    @property
    def asdict(self):
        return {
            "name": self.name,
            "wu_name": self.wu_name,
            "platform": self.platform,
            "project_url": self.project_url,
            "final_cpu_time": self.final_cpu_time,
            "final_elapsed_time": self.final_elapsed_time,
            "estimated_cpu_time_remaining": self.estimated_cpu_time_remaining,
            "state": self.state.name,
            "received_time": self.received_time,
            "report_deadline": self.report_deadline,
            "active_task": self.active_task.asdict,
        }


class SimpleGuiInfo(BaseModel):

    host: HostInfo
    projects: list[ProjectInfo]
    results: list[Result]

    class Config:
        extra = "ignore"

    @property
    def asdict(self):
        return {
            "host": self.host.asdict,
            "projects": [project.asdict for project in self.projects],
            "results": [result.asdict for result in self.results],
        }
