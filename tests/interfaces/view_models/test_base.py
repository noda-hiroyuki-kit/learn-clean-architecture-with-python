# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""ビュー モデル基底クラスのテスト."""

from dataclasses import FrozenInstanceError

import pytest

from todo_app.interfaces.view_models.base import ErrorViewModel, OperationResult


class TestErrorViewModel:
    """ErrorViewModelのテスト."""

    def test_messageとcodeが保持される(self) -> None:
        """指定したメッセージとコードが保持されることを確認する."""
        error = ErrorViewModel(message="入力が不正です", code="VALIDATION_ERROR")

        assert (error.message, error.code) == ("入力が不正です", "VALIDATION_ERROR")

    def test_codeの既定値はnoneである(self) -> None:
        """codeを省略した場合はNoneになることを確認する."""
        error = ErrorViewModel(message="エラー")

        assert error.code is None

    def test値を変更できない(self) -> None:
        """不変なビュー モデルの値を変更できないことを確認する."""
        error = ErrorViewModel(message="エラー")

        with pytest.raises(FrozenInstanceError):
            error.message = "変更"


class TestOperationResult:
    """OperationResultのテスト."""

    @pytest.mark.parametrize(
        ("success", "error"),
        [
            pytest.param(None, None, id="neither-result"),
            pytest.param("success", ErrorViewModel(message="error"), id="both-results"),
        ],
    )
    def test成功とエラーの指定が不正な場合はvalue_errorになる(
        self, success: object | None, error: ErrorViewModel | None
    ) -> None:
        """成功とエラーが両方またはいずれも指定されない場合を拒否する."""
        with pytest.raises(
            ValueError,
            match="^成功またはエラーのどちらか一方を指定してください"
            r"\(両方は指定できません\)$",
        ):
            OperationResult(success=success, error=error)

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param(False, id="false"),
            pytest.param(0, id="zero"),
            pytest.param("", id="empty-string"),
            pytest.param([], id="empty-list"),
            pytest.param({}, id="empty-dict"),
        ],
    )
    class TestSuccess:
        """成功結果のテスト."""

        @pytest.fixture
        @classmethod
        def fixture_result(cls, value: object) -> OperationResult[object]:
            """指定した値を持つ成功結果を生成する."""
            return OperationResult.succeed(value)

        def test偽値でも成功と判定される(
            self, fixture_result: OperationResult[object]
        ) -> None:
            """偽値を結果に持つ場合も成功と判定されることを確認する."""
            assert fixture_result.is_success is True

        def test成功値が保持される(
            self, fixture_result: OperationResult[object], value: object
        ) -> None:
            """指定した成功値がそのまま保持されることを確認する."""
            assert fixture_result.success is value

    class TestFail:
        """失敗結果のテスト."""

        @pytest.fixture
        @classmethod
        def fixture_result(cls) -> OperationResult[str]:
            """テスト用の失敗結果を生成する."""
            return OperationResult.fail("入力が不正です", "VALIDATION_ERROR")

        def test失敗と判定される(self, fixture_result: OperationResult[str]) -> None:
            """失敗結果が失敗と判定されることを確認する."""
            assert fixture_result.is_success is False

        def testエラー情報が保持される(
            self, fixture_result: OperationResult[str]
        ) -> None:
            """指定したエラー情報が保持されることを確認する."""
            assert fixture_result.error == ErrorViewModel(
                message="入力が不正です", code="VALIDATION_ERROR"
            )

    def test成功結果からエラーを取得するとvalue_errorになる(self) -> None:
        """成功結果にerrorが存在しない場合の例外を確認する."""
        result = OperationResult.succeed("成功")

        with pytest.raises(
            ValueError, match=r"^操作は成功しており、エラー情報は存在しません$"
        ):
            _ = result.error

    def test失敗結果から成功値を取得するとvalue_errorになる(self) -> None:
        """失敗結果に成功値が存在しない場合の例外を確認する."""
        result = OperationResult.fail("失敗")

        with pytest.raises(
            ValueError, match=r"^操作は失敗しており、成功した結果は存在しません$"
        ):
            _ = result.success
