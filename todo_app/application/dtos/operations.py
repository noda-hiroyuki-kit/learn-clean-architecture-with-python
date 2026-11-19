# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki
"""削除結果を表すDTOモジュール."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID


@dataclass(frozen=True)
class DeletionOutcome:
    """削除結果を表すDTO."""

    entity_id: UUID

    def __str__(self) -> str:
        """文字列表現を返す."""
        return f"ID: {self.entity_id} のエンティティを正常に削除しました。"
