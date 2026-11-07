# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""todo アプリケーションのapplicationの通知パッケージ."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from todo_app.domain.entities.task import Task


class NotificationPort(ABC):
    """タスクのイベントに関する通知を送信するためのインターフェース."""

    @abstractmethod
    def notify_task_completed(self, task: Task) -> None:
        """タスク完了の通知を送信する."""
        raise NotImplementedError

    @abstractmethod
    def notify_task_high_priority(self, task: Task) -> None:
        """高優先度タスクの通知を送信する."""
        raise NotImplementedError

    @abstractmethod
    def notify_task_deadline_approaching(self, task: Task, days_remaining: int) -> None:
        """締め切りが近づいたタスクの通知を送信する."""
        raise NotImplementedError
