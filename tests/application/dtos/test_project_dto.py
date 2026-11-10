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
    CreateProjectRequest,
)
from todo_app.domain.entities.project import Project
from todo_app.domain.entities.task import Task
from todo_app.domain.exceptions import ValidationError

if TYPE_CHECKING:
    from typing import Any

PROJECT_ID = "12345678-1234-5678-1234-567812345678"


class TestCreateProjectRequest:
    """CreateProjectRequestのテスト."""

    class Test正しく生成される:
        """CreateProjectRequestが正しく生成される."""

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_request(cls) -> CreateProjectRequest:
            """テスト用のCreateProjectRequestを生成する."""
            return CreateProjectRequest(
                name="プロジェクト名", description="プロジェクトの説明"
            )

        def test_nameが設定される(self, fixture_request: CreateProjectRequest) -> None:
            """nameが設定されることを確認する."""
            assert fixture_request.name == "プロジェクト名"

        def test_descriptionが設定される(
            self, fixture_request: CreateProjectRequest
        ) -> None:
            """descriptionが設定されることを確認する."""
            assert fixture_request.description == "プロジェクトの説明"

        def test_descriptionを省略すると空文字になる(self) -> None:
            """descriptionを省略すると空文字になることを確認する."""
            request = CreateProjectRequest(name="プロジェクト名")
            assert request.description == ""

        @pytest.mark.parametrize("field_name", ["name", "description"])
        def test_フィールドを変更できない(
            self, fixture_request: CreateProjectRequest, field_name: str
        ) -> None:
            """リクエストの各フィールドが変更できないことを確認する."""
            with pytest.raises(FrozenInstanceError, match=field_name):
                setattr(
                    fixture_request, field_name, getattr(fixture_request, field_name)
                )

    class TestToExecutionParamsでユースケース用のパラメータに変換できる:
        """to_execution_paramsで前後の空白を除去したパラメータに変換できる."""

        @pytest.mark.parametrize(
            ("name", "description", "expected"),
            [
                (
                    "プロジェクト名",
                    "プロジェクトの説明",
                    {"name": "プロジェクト名", "description": "プロジェクトの説明"},
                ),
                (
                    " \tプロジェクト 名\u3000",
                    "\n プロジェクトの 説明 \t",
                    {"name": "プロジェクト 名", "description": "プロジェクトの 説明"},
                ),
                ("プロジェクト名", "", {"name": "プロジェクト名", "description": ""}),
                (
                    "プロジェクト名",
                    " \t\n\u3000",
                    {"name": "プロジェクト名", "description": ""},
                ),
            ],
        )
        def test_前後の空白を除去したパラメータが返される(
            self, name: str, description: str, expected: dict[str, str]
        ) -> None:
            """内部の空白を保持し、前後の空白だけを除去して変換する."""
            request = CreateProjectRequest(name=name, description=description)
            assert request.to_execution_params() == expected

        def test_descriptionを省略して変換できる(self) -> None:
            """省略したdescriptionが空文字として変換されることを確認する."""
            request = CreateProjectRequest(name="プロジェクト名")
            assert request.to_execution_params() == {
                "name": "プロジェクト名",
                "description": "",
            }


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
