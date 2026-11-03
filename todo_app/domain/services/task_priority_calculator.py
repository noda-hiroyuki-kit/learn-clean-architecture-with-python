# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""タスクの優先度を計算するドメインサービス."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from todo_app.domain.entities.task import Task
    from todo_app.domain.entities.value_object import Priority


class TaskPriorityCalculator:
    """タスクの期限に応じた優先度を計算する."""

    @staticmethod
    def calculate_priority(task: Task) -> Priority | None:
        """優先度計算の未実装の雛形."""
