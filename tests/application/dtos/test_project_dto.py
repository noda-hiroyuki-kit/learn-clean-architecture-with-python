# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""CompleteProjectRequestのテスト."""

from typing import TYPE_CHECKING
from uuid import UUID

import pytest

from todo_app.application.dtos.project_dto import (
    MSG_MAX_LENGTH,
    CompleteProjectRequest,
)
from todo_app.domain.exceptions import ValidationError

if TYPE_CHECKING:
    from typing import Any

PROJECT_ID = "12345678-1234-5678-1234-567812345678"


class TestCompleteProjectRequest:
    """CompleteProjectRequestのテスト."""

    class Test正しく生成される:
        """CompleteProjectRequestが正しく生成される."""

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_request(cls) -> CompleteProjectRequest:
            """テスト用のCompleteProjectRequestを生成するフィクスチャ."""
            return CompleteProjectRequest(
                project_id=PROJECT_ID, completion_notes="完了メモ"
            )

        def test_project_idが設定される(
            self, fixture_request: CompleteProjectRequest
        ) -> None:
            """project_idが設定されることを確認する."""
            assert fixture_request.project_id == PROJECT_ID

        def test_completion_notesが設定される(
            self, fixture_request: CompleteProjectRequest
        ) -> None:
            """completion_notesが設定されることを確認する."""
            assert fixture_request.completion_notes == "完了メモ"

        def test_completion_notesを省略するとnoneになる(self) -> None:
            """completion_notesを省略するとNoneになることを確認する."""
            request = CompleteProjectRequest(project_id=PROJECT_ID)
            assert request.completion_notes is None

        def test_最大長ちょうどのcompletion_notesで生成できる(self) -> None:
            """最大長ちょうどのcompletion_notesで生成できることを確認する."""
            notes = "a" * MSG_MAX_LENGTH
            request = CompleteProjectRequest(
                project_id=PROJECT_ID, completion_notes=notes
            )
            assert request.completion_notes == notes

    class Test検証エラーになる:
        """不正なリクエストデータの場合はValidationErrorが送出される."""

        def test_project_idが空文字の場合はvalidation_errorになる(self) -> None:
            """project_idが空文字の場合はValidationErrorになることを確認する."""
            with pytest.raises(ValidationError, match="プロジェクト ID が必要です"):
                CompleteProjectRequest(project_id="")

        def test_project_idが空白のみの場合はvalidation_errorになる(self) -> None:
            """project_idが空白のみの場合はValidationErrorになることを確認する."""
            with pytest.raises(ValidationError, match="プロジェクト ID が必要です"):
                CompleteProjectRequest(project_id="   ")

        def test_completion_notesが最大長を超える場合はvalidation_errorになる(
            self,
        ) -> None:
            """completion_notesが最大長を超える場合はValidationErrorになることを確認する."""
            with pytest.raises(
                ValidationError,
                match=f"完了ノートは{MSG_MAX_LENGTH}文字以下としてください",
            ):
                CompleteProjectRequest(
                    project_id=PROJECT_ID,
                    completion_notes="a" * (MSG_MAX_LENGTH + 1),
                )

    class TestToExecutionParamsでユースケース用のパラメータに変換できる:
        """to_execution_paramsでユースケース用のパラメータに変換できる."""

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_params(cls) -> dict[str, Any]:
            """to_execution_paramsの変換結果を返すフィクスチャ."""
            request = CompleteProjectRequest(
                project_id=PROJECT_ID, completion_notes="完了メモ"
            )
            return request.to_execution_params()

        def test_project_idがUUIDに変換される(
            self, fixture_params: dict[str, Any]
        ) -> None:
            """project_idがUUIDに変換されることを確認する."""
            assert fixture_params["project_id"] == UUID(PROJECT_ID)

        def test_completion_notesが設定される(
            self, fixture_params: dict[str, Any]
        ) -> None:
            """completion_notesが設定されることを確認する."""
            assert fixture_params["completion_notes"] == "完了メモ"

        def test_不正な形式のproject_idの場合はvalue_errorになる(self) -> None:
            """UUID形式でないproject_idの場合はValueErrorになることを確認する."""
            request = CompleteProjectRequest(project_id="not-a-uuid")
            with pytest.raises(
                ValueError, match="badly formed hexadecimal UUID string"
            ):
                request.to_execution_params()
