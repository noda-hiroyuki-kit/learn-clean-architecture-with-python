# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""ResultとErrorのテスト."""

import pytest

from todo_app.application.common.result import Error, ErrorCode, Result


class TestError:
    """標準化されたエラー情報のテスト."""

    class TestNotFoundでエラーが生成される:
        """未検出エラーのテスト."""

        @pytest.fixture
        @classmethod
        def fixture_error(cls) -> Error:
            """テスト用の未検出エラーを生成する."""
            return Error.not_found("Project", "123")

        def test_codeがnot_foundになる(self, fixture_error: Error) -> None:
            """未検出エラーのコードが設定されることを確認する."""
            assert fixture_error.code is ErrorCode.NOT_FOUND

        def test_messageに対象の名前とidが含まれる(self, fixture_error: Error) -> None:
            """エンティティ名とIDを含むメッセージになることを確認する."""
            assert fixture_error.message == "id 123 の Project が見つかりません"

        def test_detailsがnoneになる(self, fixture_error: Error) -> None:
            """追加情報がないことを確認する."""
            assert fixture_error.details is None

    class TestValidationErrorでエラーが生成される:
        """検証エラーのテスト."""

        @pytest.fixture
        @classmethod
        def fixture_error(cls) -> Error:
            """テスト用の検証エラーを生成する."""
            return Error.validation_error("タスクのタイトルは必須です")

        def test_codeがvalidation_errorになる(self, fixture_error: Error) -> None:
            """検証エラーのコードが設定されることを確認する."""
            assert fixture_error.code is ErrorCode.VALIDATION_ERROR

        def test_messageが保持される(self, fixture_error: Error) -> None:
            """指定したメッセージが保持されることを確認する."""
            assert fixture_error.message == "タスクのタイトルは必須です"

        def test_detailsがnoneになる(self, fixture_error: Error) -> None:
            """追加情報がないことを確認する."""
            assert fixture_error.details is None


class TestResult:
    """ユースケースの成功結果と失敗結果のテスト."""

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param({"id": "123", "title": "Test Task"}, id="task-response"),
            pytest.param(False, id="false"),
            pytest.param(0, id="zero"),
            pytest.param("", id="empty-string"),
            pytest.param([], id="empty-list"),
            pytest.param({}, id="empty-dict"),
        ],
    )
    class TestSuccessで成功結果が生成される:
        """戻り値の真偽によらず成功となることのテスト."""

        @pytest.fixture
        @classmethod
        def fixture_result(cls, value: object) -> Result[object]:
            """指定した戻り値から成功結果を生成する."""
            return Result.success(value)

        def test_is_successがtrueになる(self, fixture_result: Result[object]) -> None:
            """成功と判定されることを確認する."""
            assert fixture_result.is_success is True

        def test_valueが保持される(
            self, fixture_result: Result[object], value: object
        ) -> None:
            """渡した戻り値がそのまま保持されることを確認する."""
            assert fixture_result.value is value

        def test_errorにアクセスすると例外になる(
            self, fixture_result: Result[object]
        ) -> None:
            """成功結果からエラーを取得できないことを確認する."""
            with pytest.raises(
                ValueError,
                match="成功結果からエラーにアクセスすることはできません。",
            ):
                _ = fixture_result.error

    @pytest.mark.parametrize(
        "error",
        [
            pytest.param(Error.not_found("Project", "123"), id="project-not-found"),
            pytest.param(
                Error.validation_error("タスクのタイトルは必須です"),
                id="validation-error",
            ),
        ],
    )
    class TestFailureで失敗結果が生成される:
        """未検出と検証エラーによる失敗結果のテスト."""

        @pytest.fixture
        @classmethod
        def fixture_result(cls, error: Error) -> Result[object]:
            """指定したエラーから失敗結果を生成する."""
            return Result.failure(error)

        def test_is_successがfalseになる(self, fixture_result: Result[object]) -> None:
            """失敗と判定されることを確認する."""
            assert fixture_result.is_success is False

        def test_valueにアクセスすると例外になる(
            self, fixture_result: Result[object]
        ) -> None:
            """失敗結果から値を取得できないことを確認する."""
            with pytest.raises(
                ValueError,
                match="エラー結果から値にアクセスすることはできません。",
            ):
                _ = fixture_result.value

        def test_errorが保持される(
            self, fixture_result: Result[object], error: Error
        ) -> None:
            """渡したエラーがそのまま保持されることを確認する."""
            assert fixture_result.error is error

    class TestInvalidResult:
        """値とエラーの不正な組み合わせのテスト."""

        @pytest.mark.parametrize(
            ("value", "error"),
            [
                pytest.param(None, None, id="neither-value-nor-error"),
                pytest.param(
                    "task",
                    Error.not_found("Project", "123"),
                    id="both-value-and-error",
                ),
            ],
        )
        def test値とエラーが両方またはどちらもない場合は生成できない(
            self, value: str | None, error: Error | None
        ) -> None:
            """値とエラーのどちらか一方だけが必要であることを確認する."""
            with pytest.raises(
                ValueError,
                match="値またはエラーのどちらか一方だけを設定してください。",
            ):
                Result(_value=value, _error=error)

        def test_noneを成功値として生成できない(self) -> None:
            """Noneを成功結果の値として設定できないことを確認する."""
            with pytest.raises(
                ValueError,
                match="値またはエラーのどちらか一方だけを設定してください。",
            ):
                Result.success(None)
