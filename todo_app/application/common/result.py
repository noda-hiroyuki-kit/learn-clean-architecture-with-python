# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""todo アプリケーションのapplicationの共通の結果モジュール."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Self


class ErrorCode(Enum):
    """エラーコードの列挙型."""

    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    # Add other error codes as needed


@dataclass(frozen=True)
class Error:
    """標準化されたエラー情報."""

    code: ErrorCode
    message: str
    details: dict[str, Any] | None = None

    @classmethod
    def not_found(cls, entity: str, entity_id: str) -> Self:
        """指定されたエンティティが見つからなかった場合のエラーを生成する."""
        return cls(
            code=ErrorCode.NOT_FOUND,
            message=f"id {entity_id} の {entity} が見つかりません",
        )

    @classmethod
    def validation_error(cls, message: str) -> Self:
        """バリデーションエラーを生成する."""
        return cls(code=ErrorCode.VALIDATION_ERROR, message=message)
