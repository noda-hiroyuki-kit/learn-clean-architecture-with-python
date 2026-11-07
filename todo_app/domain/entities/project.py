# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.

"""Projectエンティティ."""

import datetime as dt
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from todo_app.domain.entities.entity import Entity
from todo_app.domain.value_object import ProjectStatus, TaskStatus

if TYPE_CHECKING:
    from uuid import UUID

    from todo_app.domain.entities.task import Task


@dataclass
class Project(Entity):
    """Projectエンティティ."""

    name: str
    description: str = ""
    status: ProjectStatus = field(default=ProjectStatus.ACTIVE, init=False)
    completed_at: dt.datetime | None = field(default=None, init=False)
    completion_notes: str | None = field(default=None, init=False)
    _tasks: dict[UUID, Task] = field(default_factory=dict, init=False)

    def add_task(self, task: Task) -> None:
        """タスクを追加する."""
        if self.status == ProjectStatus.COMPLETED:
            msg = "完了したプロジェクトにはタスクを追加できません"
            raise ValueError(msg)
        self._tasks[task.id] = task
        task.project_id = self.id

    def remove_task(self, task_id: UUID) -> None:
        """タスクを削除する."""
        if task := self._tasks.pop(task_id, None):
            task.project_id = None

    def get_task(self, task_id: UUID) -> Task | None:
        """タスクを取得する."""
        return self._tasks.get(task_id)

    @property
    def tasks(self) -> list[Task]:
        """タスクの一覧を取得する."""
        return list(self._tasks.values())

    @property
    def incomplete_tasks(self) -> list[Task]:
        """未完了のタスクの一覧を取得する."""
        return [task for task in self.tasks if task.status != TaskStatus.DONE]

    def mark_completed(self, notes: str | None = None) -> None:
        """プロジェクトを完了済みにする.

        Args:
            notes (str | None): 完了時のメモ.

        """
        if self.status == ProjectStatus.COMPLETED:
            return
        self.status = ProjectStatus.COMPLETED
        self.completed_at = dt.datetime.now(tz=dt.UTC)
        self.completion_notes = notes
