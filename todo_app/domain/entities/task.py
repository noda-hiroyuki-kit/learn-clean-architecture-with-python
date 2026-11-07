# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""Taskエンティティ."""

import datetime as dt
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from todo_app.domain.entities.entity import Entity
from todo_app.domain.value_object import Deadline, Priority, TaskStatus

if TYPE_CHECKING:
    from uuid import UUID


@dataclass
class Task(Entity):
    """Taskエンティティ."""

    title: str
    description: str
    due_date: Deadline | None = None
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = field(default=TaskStatus.TODO, init=False)
    completed_at: dt.datetime | None = field(default=None, init=False)
    completion_notes: str | None = field(default=None, init=False)
    project_id: UUID | None = field(default=None, init=False)

    def start(self) -> None:
        """Taskを開始する.

        Raises
        ------
        ValueError
            Taskがすでに進行中または完了している場合.

        """
        if self.status != TaskStatus.TODO:
            msg = "TaskのstatusがTODOの場合のみ開始できます。"
            raise ValueError(msg)
        self.status = TaskStatus.IN_PROGRESS

    def complete(self, notes: str | None = None) -> None:
        """Taskを完了する.

        Raises
        ------
        ValueError
            Taskが既に完了している場合.

        """
        if self.status == TaskStatus.DONE:
            msg = "Taskは既に完了しています。"
            raise ValueError(msg)
        self.status = TaskStatus.DONE
        self.completed_at = dt.datetime.now(tz=dt.UTC)
        self.completion_notes = notes

    def is_overdue(self) -> bool:
        """Taskの期限が過ぎているかを判定する.

        Returns
        -------
        bool
            期限が過ぎている場合はTrue、それ以外はFalse.

        """
        return self.due_date is not None and self.due_date.is_overdue()
