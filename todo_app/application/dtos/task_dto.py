# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""アプリケーション層のための Task データ転送オブジェクト."""

import datetime as dt
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self
from uuid import UUID

from todo_app.domain.value_object import Deadline, Priority, TaskStatus

if TYPE_CHECKING:
    from todo_app.domain.entities.task import Task


@dataclass(frozen=True)
class CompleteTaskRequest:
    """タスク完了のリクエストデータ."""

    task_id: str
    completion_notes: str | None = None

    def __post_init__(self) -> None:
        """リクエストデータを検証する."""
        if not self.task_id.strip():
            msg = "タスク ID が必要です"
            raise ValueError(msg)
        try:
            UUID(self.task_id)
        except ValueError:
            msg = "タスク ID の形式が無効です"
            raise ValueError(msg) from None

    def to_execution_params(self) -> dict:
        """リクエストデータをユースケースのパラメータに変換する."""
        return {
            "task_id": UUID(self.task_id),
            "completion_notes": self.completion_notes,
        }


@dataclass(frozen=True)
class CreateTaskRequest:
    """タスク作成のリクエストデータ."""

    title: str
    description: str
    due_date: str | None = None
    priority: str | None = None
    project_id: str | None = None

    def __post_init__(self) -> None:
        """リクエストデータを検証する."""
        if self.priority is not None:
            try:
                _normalize_priority(self.priority)
            except AttributeError, ValueError:
                msg = "優先度は次のいずれかである必要があります: "
                msg += f"{', '.join(p.name for p in Priority)}"
                raise ValueError(msg) from None
        if self.project_id:
            try:
                UUID(self.project_id)
            except ValueError:
                msg = "プロジェクト ID の形式が無効です"
                raise ValueError(msg) from None

    def to_execution_params(self) -> dict:
        """リクエストデータをユースケースのパラメータに変換する."""
        params = {
            "title": self.title.strip(),
            "description": self.description.strip(),
        }

        if self.due_date:
            params["due_date"] = Deadline(dt.datetime.fromisoformat(self.due_date))
        if self.priority:
            params["priority"] = Priority[_normalize_priority(self.priority)]
        if self.project_id:
            params["project_id"] = UUID(self.project_id)

        return params


def _normalize_priority(priority: str) -> str:
    """優先度を正規化して検証する."""
    priority_value = priority.strip().upper()
    if not priority_value or priority_value not in [p.name for p in Priority]:
        raise ValueError
    return priority_value


@dataclass(frozen=True)
class TaskResponse:
    """Taskのレスポンスデータ."""

    id: str  # UUID conversion needed for boundary crossing
    title: str
    description: str
    status: TaskStatus
    priority: Priority
    due_date: dt.datetime | None = None
    project_id: str | None = None
    completion_date: dt.datetime | None = None
    completion_notes: str | None = None

    @classmethod
    def from_entity(cls, task: Task) -> Self:
        """taskエンティティからレスポンスを作成する."""
        return cls(
            id=str(task.id),  # Basic conversion for boundary crossing
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date.due_date if task.due_date else None,
            project_id=str(task.project_id) if task.project_id else None,
            completion_date=task.completed_at,
            completion_notes=task.completion_notes,
        )


@dataclass(frozen=True)
class SetTaskPriorityRequest:
    """タスクの優先度を更新するためのリクエストデータ."""

    task_id: str
    priority: str

    def __post_init__(self) -> None:
        """リクエストデータを検証する."""
        if not self.task_id.strip():
            msg = "タスク ID が必要です"
            raise ValueError(msg)
        try:
            _normalize_priority(self.priority)
        except AttributeError, ValueError:
            msg = "優先度は次のいずれかである必要があります: "
            msg += f"{', '.join(p.name for p in Priority)}"
            raise ValueError(msg) from None
        try:
            UUID(self.task_id)
        except ValueError:
            msg = "タスク ID の形式が無効です"
            raise ValueError(msg) from None

    def to_execution_params(self) -> dict:
        """リクエストデータをユースケースのパラメータに変換する."""
        return {
            "task_id": UUID(self.task_id),
            "priority": Priority[_normalize_priority(self.priority)],
        }


@dataclass(frozen=True)
class UpdateTaskRequest:
    """タスクを更新するためのリクエストデータ."""

    task_id: str
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: Priority | None = None
    due_date: str | None = None

    def to_execution_params(self) -> dict:
        """リクエストデータをユースケースのパラメータに変換する.

        Returns:
            dict: ユースケースの実行に必要なパラメータを含む辞書.

        """
        params = {"task_id": UUID(self.task_id)}

        if self.title is not None:
            params["title"] = self.title.strip()
        if self.description is not None:
            params["description"] = self.description.strip()
        if self.status is not None:
            params["status"] = self.status
        if self.priority is not None:
            params["priority"] = self.priority
        # Always include deadline in params if due_date was provided
        if self.due_date is not None:
            if self.due_date:  # Non-empty string
                due_date = dt.datetime.fromisoformat(self.due_date)
                if not due_date.tzinfo:
                    due_date = due_date.replace(tzinfo=dt.UTC)
                params["deadline"] = Deadline(due_date)
            else:  # Empty string - clear the deadline
                params["deadline"] = None

        return params
