# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""Projectエンティティの永続化のためのリポジトリインターフェースを定義するモジュール."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from todo_app.domain.entities.project import Project


class ProjectRepository(ABC):
    """Projectエンティティの永続化のためのリポジトリインターフェース."""

    @abstractmethod
    def get(self, project_id: UUID) -> Project:
        """IDを指定してProjectを取得する.

        Parameters
        ----------
        project_id : UUID
            Projectの一意な識別子.

        Returns
        -------
        Project
            要求されたProjectエンティティ.

        Raises
        ------
        ProjectNotFoundError
            指定されたIDのProjectが存在しない場合.

        """
        raise NotImplementedError

    @abstractmethod
    def save(self, project: Project) -> None:
        """Projectをリポジトリに保存する.

        Parameters
        ----------
        project : Project
            保存するProjectエンティティ.

        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, project_id: UUID) -> None:
        """Projectをリポジトリから削除する.

        Parameters
        ----------
        project_id : UUID
            削除するProjectの一意な識別子.

        Raises
        ------
        ProjectNotFoundError
            指定されたIDのProjectが存在しない場合.

        """
        raise NotImplementedError
