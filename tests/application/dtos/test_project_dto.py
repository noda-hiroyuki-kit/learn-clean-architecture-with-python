# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""Projectデータ転送オブジェクトのテスト."""

import datetime as dt
from dataclasses import FrozenInstanceError
from typing import TYPE_CHECKING
from uuid import UUID

import pytest

from todo_app.application.dtos.project_dto import (
    MSG_MAX_LENGTH,
    CompleteProjectRequest,
    CompleteProjectResponse,
)
from todo_app.domain.entities.project import Project
from todo_app.domain.entities.task import Task
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


class TestCompleteProjectResponse:
    """CompleteProjectResponseのテスト."""

    class TestFromEntityでレスポンスに変換できる:
        """from_entityで完了済みプロジェクトをレスポンスに変換できる."""

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_response(cls) -> CompleteProjectResponse:
            """完了日時とタスクを指定したプロジェクトのレスポンスを返すフィクスチャ."""
            project = Project(name="テストプロジェクト")
            project.id = UUID(PROJECT_ID)
            project.add_task(Task(title="タスク1", description="説明1"))
            project.add_task(Task(title="タスク2", description="説明2"))
            project.mark_completed(notes="完了メモ")
            project.completed_at = dt.datetime(
                2026, 1, 2, 3, 4, 5, 123456, tzinfo=dt.UTC
            )
            return CompleteProjectResponse.from_entity(project)

        def test_idが文字列に変換される(
            self, fixture_response: CompleteProjectResponse
        ) -> None:
            """プロジェクトのUUIDが文字列に変換されることを確認する."""
            assert fixture_response.id == PROJECT_ID

        def test_statusが列挙型の値に変換される(
            self, fixture_response: CompleteProjectResponse
        ) -> None:
            """プロジェクトのstatusが列挙型の値に変換されることを確認する."""
            assert fixture_response.status == "COMPLETED"

        def test_completion_dateがiso形式に変換される(
            self, fixture_response: CompleteProjectResponse
        ) -> None:
            """完了日時がタイムゾーンとマイクロ秒を含むISO形式になることを確認する."""
            expected_date = "2026-01-02T03:04:05.123456+00:00"
            assert fixture_response.completion_date == expected_date

        def test_task_countが設定される(
            self, fixture_response: CompleteProjectResponse
        ) -> None:
            """プロジェクトのタスク数が設定されることを確認する."""
            expected_count = 2
            assert fixture_response.task_count == expected_count

        def test_completion_notesが設定される(
            self, fixture_response: CompleteProjectResponse
        ) -> None:
            """プロジェクトの完了メモが設定されることを確認する."""
            assert fixture_response.completion_notes == "完了メモ"

        @pytest.mark.parametrize(
            "field_name",
            ["id", "status", "completion_date", "task_count", "completion_notes"],
        )
        def test_フィールドを変更できない(
            self, fixture_response: CompleteProjectResponse, field_name: str
        ) -> None:
            """レスポンスの各フィールドが変更できないことを確認する."""
            with pytest.raises(FrozenInstanceError, match=field_name):
                setattr(
                    fixture_response, field_name, getattr(fixture_response, field_name)
                )

        def test_タスクがない場合はtask_countがゼロになる(self) -> None:
            """タスクがないプロジェクトのtask_countがゼロになることを確認する."""
            project = Project(name="タスクのないプロジェクト")
            project.mark_completed()
            response = CompleteProjectResponse.from_entity(project)
            assert response.task_count == 0

        @pytest.mark.parametrize("notes", [None, ""])
        def test_完了メモが未指定または空文字でも保持される(
            self, notes: str | None
        ) -> None:
            """完了メモのNoneと空文字が変換後も保持されることを確認する."""
            project = Project(name="テストプロジェクト")
            project.mark_completed(notes=notes)
            response = CompleteProjectResponse.from_entity(project)
            assert response.completion_notes == notes

    class TestFromEntityで検証エラーになる:
        """from_entityで未完了プロジェクトを変換するとエラーになる."""

        def test_未完了の場合はvalue_errorになる(self) -> None:
            """完了日時がないプロジェクトの場合はValueErrorになることを確認する."""
            project = Project(name="未完了プロジェクト")
            with pytest.raises(ValueError, match="プロジェクトは完了していません"):
                CompleteProjectResponse.from_entity(project)
