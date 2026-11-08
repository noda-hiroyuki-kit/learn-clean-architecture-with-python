# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""アプリケーション層のための Project データ転送オブジェクト."""

from dataclasses import dataclass
from uuid import UUID

from todo_app.domain.exceptions import ValidationError

MSG_MAX_LENGTH = 1000


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
