# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""Taskデータ転送オブジェクトのテスト."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import UUID

import pytest

from todo_app.application.dtos.task_dto import SetTaskPriorityRequest, TaskResponse
from todo_app.domain.entities.task import Task
from todo_app.domain.value_object import Deadline, Priority, TaskStatus

TASK_ID = "12345678-1234-5678-1234-567812345678"
PROJECT_ID = "87654321-4321-8765-4321-876543218765"


class TestTaskResponse:
    """TaskResponseのテスト."""

    class TestFromEntityでレスポンスに変換できる:
        """from_entityでTaskをレスポンスに変換できる."""

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_response(cls) -> TaskResponse:
            """全フィールドを設定したTaskのレスポンスを返す."""
            due_date = datetime(2026, 12, 31, 12, tzinfo=UTC)
            completed_at = datetime(2026, 11, 1, 10, tzinfo=UTC)
            task = Task(
                title="テストタスク",
                description="タスクの説明",
                due_date=Deadline(due_date),
                priority=Priority.HIGH,
            )
            task.id = UUID(TASK_ID)
            task.project_id = UUID(PROJECT_ID)
            task.status = TaskStatus.DONE
            task.completed_at = completed_at
            task.completion_notes = "完了メモ"
            return TaskResponse.from_entity(task)

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_response_without_optional_fields(cls) -> TaskResponse:
            """任意フィールドのないTaskのレスポンスを返す."""
            task = Task(title="タスク", description="説明")
            return TaskResponse.from_entity(task)

        def test_idが文字列に変換される(self, fixture_response: TaskResponse) -> None:
            """TaskのUUIDが文字列に変換されることを確認する."""
            assert fixture_response.id == TASK_ID

        def test_titleが設定される(self, fixture_response: TaskResponse) -> None:
            """titleがレスポンスに設定されることを確認する."""
            assert fixture_response.title == "テストタスク"

        def test_descriptionが設定される(self, fixture_response: TaskResponse) -> None:
            """descriptionがレスポンスに設定されることを確認する."""
            assert fixture_response.description == "タスクの説明"

        def test_statusが設定される(self, fixture_response: TaskResponse) -> None:
            """statusがレスポンスに設定されることを確認する."""
            assert fixture_response.status == TaskStatus.DONE

        def test_priorityが設定される(self, fixture_response: TaskResponse) -> None:
            """priorityがレスポンスに設定されることを確認する."""
            assert fixture_response.priority == Priority.HIGH

        def test_due_dateが設定される(self, fixture_response: TaskResponse) -> None:
            """期限日時がレスポンスに設定されることを確認する."""
            assert fixture_response.due_date == datetime(2026, 12, 31, 12, tzinfo=UTC)

        def test_project_idが文字列に変換される(
            self, fixture_response: TaskResponse
        ) -> None:
            """project_idのUUIDが文字列に変換されることを確認する."""
            assert fixture_response.project_id == PROJECT_ID

        def test_completion_dateが設定される(
            self, fixture_response: TaskResponse
        ) -> None:
            """完了日時がレスポンスに設定されることを確認する."""
            assert fixture_response.completion_date == datetime(
                2026, 11, 1, 10, tzinfo=UTC
            )

        def test_completion_notesが設定される(
            self, fixture_response: TaskResponse
        ) -> None:
            """完了メモがレスポンスに設定されることを確認する."""
            assert fixture_response.completion_notes == "完了メモ"

        def test任意フィールドがない場合はnoneになる(
            self, fixture_response_without_optional_fields: TaskResponse
        ) -> None:
            """任意フィールドがない場合はNoneに変換されることを確認する."""
            response = fixture_response_without_optional_fields
            assert (
                response.due_date,
                response.project_id,
                response.completion_date,
                response.completion_notes,
            ) == (None, None, None, None)

        @pytest.mark.parametrize(
            "field_name",
            [
                "id",
                "title",
                "description",
                "status",
                "priority",
                "due_date",
                "project_id",
                "completion_date",
                "completion_notes",
            ],
        )
        def testフィールドを変更できない(
            self, fixture_response: TaskResponse, field_name: str
        ) -> None:
            """レスポンスの各フィールドが変更できないことを確認する."""
            with pytest.raises(FrozenInstanceError, match=field_name):
                setattr(
                    fixture_response, field_name, getattr(fixture_response, field_name)
                )


class TestSetTaskPriorityRequest:
    """SetTaskPriorityRequestのテスト."""

    class Test正しく生成される:
        """SetTaskPriorityRequestが正しく生成される."""

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_request(cls) -> SetTaskPriorityRequest:
            """テスト用のSetTaskPriorityRequestを生成する."""
            return SetTaskPriorityRequest(task_id=TASK_ID, priority="HIGH")

        def test_task_idが設定される(
            self, fixture_request: SetTaskPriorityRequest
        ) -> None:
            """task_idが設定されることを確認する."""
            assert fixture_request.task_id == TASK_ID

        def test_priorityが設定される(
            self, fixture_request: SetTaskPriorityRequest
        ) -> None:
            """priorityが設定されることを確認する."""
            assert fixture_request.priority == "HIGH"

        def test_フィールドを変更できない(
            self, fixture_request: SetTaskPriorityRequest
        ) -> None:
            """リクエストのフィールドが変更できないことを確認する."""
            with pytest.raises(FrozenInstanceError, match="priority"):
                fixture_request.priority = "LOW"

    class Test検証エラーになる:
        """不正なリクエストデータの場合はValueErrorが送出される."""

        @pytest.mark.parametrize("task_id", ["", "   "])
        def test_task_idが空の場合はvalue_errorになる(self, task_id: str) -> None:
            """task_idが空または空白のみの場合はValueErrorになることを確認する."""
            with pytest.raises(ValueError, match="タスク ID が必要です"):
                SetTaskPriorityRequest(task_id=task_id, priority="HIGH")

        def test_task_idがuuid形式でない場合はvalue_errorになる(self) -> None:
            """task_idがUUID形式でない場合はValueErrorになることを確認する."""
            with pytest.raises(ValueError, match="タスク ID の形式が無効です"):
                SetTaskPriorityRequest(task_id="not-a-uuid", priority="HIGH")

        @pytest.mark.parametrize("priority", ["", "UNKNOWN"])
        def test_priorityが無効な場合はvalue_errorになる(self, priority: str) -> None:
            """priorityが有効な優先度でない場合はValueErrorになることを確認する."""
            with pytest.raises(ValueError, match="優先度は次のいずれか"):
                SetTaskPriorityRequest(task_id=TASK_ID, priority=priority)

    class TestToExecutionParamsでユースケース用のパラメータに変換できる:
        """to_execution_paramsでユースケース用のパラメータに変換できる."""

        @pytest.mark.parametrize(
            ("priority", "expected_priority"),
            [
                ("LOW", Priority.LOW),
                ("medium", Priority.MEDIUM),
                (" high　", Priority.HIGH),
            ],
        )
        def test_task_idがuuidに変換され優先度が正規化される(
            self, priority: str, expected_priority: Priority
        ) -> None:
            """task_idをUUIDに変換し、優先度の大小文字と空白を正規化する."""
            request = SetTaskPriorityRequest(task_id=TASK_ID, priority=priority)
            params = request.to_execution_params()
            assert params == {
                "task_id": UUID(TASK_ID),
                "priority": expected_priority,
            }
