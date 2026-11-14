# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""タスクの優先度を計算するドメインサービス."""

import datetime as dt
from typing import TYPE_CHECKING

from todo_app.domain.value_object import Priority

if TYPE_CHECKING:
    from todo_app.domain.entities.task import Task


class TaskPriorityCalculator:
    """タスクの期限に応じた優先度を計算する."""

    @staticmethod
    def calculate_priority(task: Task) -> Priority | None:
        """優先度計算の未実装の雛形."""
        if task.due_date is None:
            return task.priority
        if task.is_overdue() or task.due_date.time_remaining() <= dt.timedelta(
            hours=12
        ):
            return Priority.HIGH
        if task.due_date and task.due_date.time_remaining() <= dt.timedelta(days=2):
            return Priority.MEDIUM
        return Priority.LOW
