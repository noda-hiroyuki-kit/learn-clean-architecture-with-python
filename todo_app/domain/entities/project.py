# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.

"""Projectエンティティ."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from todo_app.domain.entities.entity import Entity
from todo_app.domain.value_object import ProjectStatus

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID

    from todo_app.domain.entities.task import Task


@dataclass
class Project(Entity):
    """Projectエンティティ."""

    name: str
    description: str = ""
    status: ProjectStatus = field(default=ProjectStatus.ACTIVE, init=False)
    completed_at: datetime | None = field(default=None, init=False)
    completion_notes: str | None = field(default=None, init=False)
    _tasks: dict[UUID, Task] = field(default_factory=dict, init=False)

    def add_task(self, task: Task) -> None:
        """タスクを追加する."""
        self._tasks[task.id] = task

    def remove_task(self, task_id: UUID) -> None:
        """タスクを削除する."""
        self._tasks.pop(task_id, None)

    def get_task(self, task_id: UUID) -> Task | None:
        """タスクを取得する."""
        return self._tasks.get(task_id)

    @property
    def tasks(self) -> list[Task]:
        """タスクの一覧を取得する."""
        return list(self._tasks.values())
