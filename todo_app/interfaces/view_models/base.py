# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""ビュー モデル 基底モジュール."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorViewModel:
    """エラーのビュー モデル."""

    message: str
    code: str | None = None


@dataclass
class OperationResult[T]:
    """操作結果のビュー モデルの基底クラス."""

    _success: T | None = None
    _error: ErrorViewModel | None = None

    def __init__(
        self, success: T | None = None, error: ErrorViewModel | None = None
    ) -> None:
        """初期化.

        Args:
            success (T | None): 成功した操作結果の値
            error (ErrorViewModel | None): エラー情報

        """
        self._success = success
        self._error = error

    @classmethod
    def succeed(cls, value: T) -> OperationResult[T]:
        """与えられた値で成功した結果を作成する.

        Args:
            value (T): 成功した操作結果の値

        Returns:
            OperationResult[T]: 成功した操作結果

        """
        return cls(success=value)

    @classmethod
    def fail(cls, message: str, code: str | None = None) -> OperationResult[T]:
        """与えられたエラーメッセージとコードから失敗した操作結果を作成する.

        Args:
            message (str): エラーメッセージ
            code (str | None): エラーコード

        Returns:
            OperationResult[T]: 失敗した操作結果

        """
        return cls(error=ErrorViewModel(message=message, code=code))
