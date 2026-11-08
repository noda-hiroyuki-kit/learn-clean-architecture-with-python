# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""アプリケーション層のための Task データ転送オブジェクト."""

from dataclasses import dataclass
from uuid import UUID

from todo_app.domain.value_object import Priority


def _normalize_priority(priority: str) -> str:
    """優先度を正規化して検証する."""
    priority_value = priority.strip().upper()
    if not priority_value or priority_value not in [p.name for p in Priority]:
        raise ValueError
    return priority_value


@dataclass(frozen=True)
class SetTaskPriorityRequest:
    """タスクの優先度を更新するためのリクエストデータ."""

    task_id: str
    priority: str

    def __post_init__(self) -> None:
        """リクエストデータを検証する."""
        if not self.task_id.strip():
            msg = "タスク ID が必要です"
            raise ValueError(msg)
        try:
            _normalize_priority(self.priority)
        except AttributeError, ValueError:
            msg = "優先度は次のいずれかである必要があります: "
            msg += f"{', '.join(p.name for p in Priority)}"
            raise ValueError(msg) from None
        try:
            UUID(self.task_id)
        except ValueError:
            msg = "タスク ID の形式が無効です"
            raise ValueError(msg) from None

    def to_execution_params(self) -> dict:
        """リクエストデータをユースケースのパラメータに変換する."""
        return {
            "task_id": UUID(self.task_id),
            "priority": Priority[_normalize_priority(self.priority)],
        }
