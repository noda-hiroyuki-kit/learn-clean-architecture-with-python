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
    """操作結果のビュー モデルクラス."""

    _success: T | None = None
    _error: ErrorViewModel | None = None

    def __init__(
        self, success: T | None = None, error: ErrorViewModel | None = None
    ) -> None:
        """初期化.

        Args:
            success (T | None): 成功した操作結果の値
            error (ErrorViewModel | None): エラー情報

        Raises:
            ValueError:
                成功またはエラーのどちらか一方が指定されていない場合、または両方が指定された場合

        """
        if (success is None and error is None) or (
            success is not None and error is not None
        ):
            msg = (
                "成功またはエラーのどちらか一方を指定してください(両方は指定できません)"
            )
            raise ValueError(msg)
        self._success = success
        self._error = error

    @property
    def is_success(self) -> bool:
        """操作が成功したかどうかを返す."""
        return self._success is not None

    @property
    def success(self) -> T:
        """成功した操作結果の値を返す.

        Returns:
            T: 成功した操作結果の値

        Raises:
            ValueError: 操作が失敗しており、成功した結果が存在しない場合

        """
        if self._success is None:
            msg = "操作は失敗しており、成功した結果は存在しません"
            raise ValueError(msg)
        return self._success

    @property
    def error(self) -> ErrorViewModel:
        """エラー情報を返す.

        Returns:
            ErrorViewModel: エラー情報

        Raises:
            ValueError: 操作が成功しており、エラー情報が存在しない場合

        """
        if self._error is None:
            msg = "操作は成功しており、エラー情報は存在しません"
            raise ValueError(msg)
        return self._error

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
