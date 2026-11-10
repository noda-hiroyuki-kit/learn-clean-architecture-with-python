# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""アプリケーション層のための Project データ転送オブジェクト."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self
from uuid import UUID

from todo_app.application.dtos.task_dto import TaskResponse
from todo_app.domain.exceptions import ValidationError

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from todo_app.domain.entities.project import Project

MSG_MAX_LENGTH = 1000


@dataclass(frozen=True)
class CreateProjectRequest:
    """プロジェクト作成リクエスト用のデータ構造."""

    name: str
    description: str = ""

    def to_execution_params(self) -> dict:
        """検証済みのリクエストデータをユースケース用のパラメータに変換."""
        return {
            "name": self.name.strip(),
            "description": self.description.strip(),
        }


@dataclass(frozen=True)
class CompleteProjectRequest:
    """プロジェクト完了リクエスト用のデータ構造."""

    project_id: str  # APIからの入力 (UUIDに変換される)
    completion_notes: str | None = None

    def __post_init__(self) -> None:
        """リクエストデータを検証."""
        if not self.project_id.strip():
            msg = "プロジェクト ID が必要です"
            raise ValidationError(msg)

        if self.completion_notes and len(self.completion_notes) > MSG_MAX_LENGTH:
            msg = f"完了ノートは{MSG_MAX_LENGTH}文字以下としてください"
            raise ValidationError(msg)

    def to_execution_params(self) -> dict:
        """検証済みのリクエストデータをユースケース用のパラメータに変換."""
        return {
            "project_id": UUID(self.project_id),
            "completion_notes": self.completion_notes,
        }


@dataclass(frozen=True)
class ProjectResponse:
    """プロジェクトのレスポンス用のデータ構造."""

    id: str
    name: str
    description: str
    status: str
    completed_date: datetime | None
    tasks: Sequence[TaskResponse]

    @classmethod
    def from_entity(cls, project: Project) -> Self:
        """ドメインエンティティからレスポンスを生成."""
        return cls(
            id=str(project.id),
            name=project.name,
            description=project.description,
            status=project.status.value,
            completed_date=project.completed_at or None,
            tasks=[TaskResponse.from_entity(t) for t in project.tasks],
        )


@dataclass(frozen=True)
class CompleteProjectResponse:
    """プロジェクト完了のレスポンス用のデータ構造."""

    id: str
    status: str
    completion_date: str
    task_count: int
    completion_notes: str | None

    @classmethod
    def from_entity(cls, project: Project) -> Self:
        """ドメインエンティティからレスポンスを生成."""
        if project.completed_at is None:
            msg = "プロジェクトは完了していません"
            raise ValueError(msg)
        return cls(
            id=str(project.id),
            status=project.status.value,
            completion_date=project.completed_at.isoformat(),
            task_count=len(project.tasks),
            completion_notes=project.completion_notes,
        )
