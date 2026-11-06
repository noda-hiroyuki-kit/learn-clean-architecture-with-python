# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""Taskエンティティの永続化のためのリポジトリインターフェースを定義するモジュール."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from uuid import UUID

    from todo_app.domain.entities.task import Task


class TaskRepository(ABC):
    """Taskエンティティの永続化のためのリポジトリインターフェース."""

    @abstractmethod
    def get(self, task_id: UUID) -> Task:
        """IDを指定してTaskを取得する.

        Parameters
        ----------
        task_id : UUID
            Taskの一意な識別子.

        Returns
        -------
        Task
            要求されたTaskエンティティ.

        Raises
        ------
        TaskNotFoundError
            指定されたIDのTaskが存在しない場合.

        """
        raise NotImplementedError

    @abstractmethod
    def save(self, task: Task) -> None:
        """Taskをリポジトリに保存する.

        Parameters
        ----------
        task : Task
            保存するTaskエンティティ.

        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, task_id: UUID) -> None:
        """Taskをリポジトリから削除する.

        Parameters
        ----------
        task_id : UUID
            削除するTaskの一意な識別子.

        """
        raise NotImplementedError

    @abstractmethod
    def find_by_project(self, project_id: UUID) -> Sequence[Task]:
        """Projectに関連付けられたすべてのTaskを検索する.

        Parameters
        ----------
        project_id : UUID
            Projectの一意な識別子.

        Returns
        -------
        Sequence[Task]
            Projectに属するTaskエンティティのシーケンス.

        """
        raise NotImplementedError

    @abstractmethod
    def get_active_tasks(self) -> Sequence[Task]:
        """リポジトリ内のすべてのアクティブなTaskを取得する.

        Returns
        -------
        Sequence[Task]
            すべてのアクティブなTaskのシーケンス.

        """
        raise NotImplementedError
