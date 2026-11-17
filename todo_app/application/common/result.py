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
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
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

    @classmethod
    def business_rule_violation(cls, message: str) -> Self:
        """Create a BUSINESS_RULE_VIOLATION error with the specified message."""
        return cls(code=ErrorCode.BUSINESS_RULE_VIOLATION, message=message)


@dataclass(frozen=True)
class Result[T]:
    """ユースケースの実行結果を表すクラス.

    成功時は_valueに値が設定され、_errorはNone。
    失敗時は_errorにエラーが設定され、_valueはNone。
    """

    _value: T | None = None
    _error: Error | None = None

    def __post_init__(self) -> None:
        """値とエラーの整合性をチェックする."""
        if (self._value is None and self._error is None) or (
            self._value is not None and self._error is not None
        ):
            msg = "値またはエラーのどちらか一方だけを設定してください。"
            raise ValueError(msg)

    @property
    def is_success(self) -> bool:
        """ユースケースの実行が成功したかどうかを返す."""
        return self._error is None

    @property
    def value(self) -> T:
        """成功結果から値を取得する.

        Raises:
            ValueError: エラー結果から値にアクセスしようとした場合

        Returns:
            T: 成功結果の値

        """
        if self._value is None:
            msg = "エラー結果から値にアクセスすることはできません。"
            raise ValueError(msg)
        return self._value

    @property
    def error(self) -> Error:
        """失敗結果からエラーを取得する.

        Raises:
            ValueError: 成功結果からエラーにアクセスしようとした場合

        Returns:
            Error: 失敗結果のエラー

        """
        if self._error is None:
            msg = "成功結果からエラーにアクセスすることはできません。"
            raise ValueError(msg)
        return self._error

    @classmethod
    def success(cls, value: T) -> Result[T]:
        """成功結果を生成する."""
        return cls(_value=value)

    @classmethod
    def failure(cls, error: Error) -> Result[T]:
        """失敗結果を生成する."""
        return cls(_error=error)
