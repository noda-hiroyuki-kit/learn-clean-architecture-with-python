# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""ToDo アプリケーション固有のドメイン例外を定義します.

これらの例外は、ドメインモデルに固有のエラー状態を表します.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID


class DomainError(Exception):
    """ドメイン固有のエラーの基底クラス."""


class TaskNotFoundError(DomainError):
    """存在しないタスクにアクセスしようとした場合に発生."""

    def __init__(self, task_id: UUID) -> None:
        """タスク ID を保持し、タスクが見つからない旨を示す例外を初期化."""
        self.task_id = task_id
        super().__init__(f"id {task_id} のタスクは見つかりません.")


class ValidationError(DomainError):
    """ドメインの検証ルールに違反した場合に発生."""


class ProjectNotFoundError(DomainError):
    """存在しないプロジェクトにアクセスしようとした場合に発生."""

    def __init__(self, project_id: UUID) -> None:
        """プロジェクト ID を保持し、プロジェクトが見つからない旨を示す例外を初期化."""
        self.project_id = project_id
        super().__init__(f"id {project_id} のプロジェクトは見つかりません.")


class BusinessRuleViolationError(DomainError):
    """ビジネスルールに違反した場合に発生."""
