# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""アプリケーション層のための Task データ転送オブジェクト."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self
from uuid import UUID

from todo_app.domain.value_object import Priority, TaskStatus

if TYPE_CHECKING:
    from datetime import datetime

    from todo_app.domain.entities.task import Task


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
    due_date: datetime | None = None
    project_id: str | None = None
    completion_date: datetime | None = None
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
