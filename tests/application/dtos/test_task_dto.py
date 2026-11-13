# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""Taskデータ転送オブジェクトのテスト."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from todo_app.application.dtos.task_dto import (
    CompleteTaskRequest,
    CreateTaskRequest,
    SetTaskPriorityRequest,
    TaskResponse,
)
from todo_app.domain.entities.task import Task
from todo_app.domain.value_object import Deadline, Priority, TaskStatus

TASK_ID = "12345678-1234-5678-1234-567812345678"
PROJECT_ID = "87654321-4321-8765-4321-876543218765"


class TestCompleteTaskRequest:
    """CompleteTaskRequestのテスト."""

    class Test正しく生成される:
        """CompleteTaskRequestが正しく生成される."""

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_request(cls) -> CompleteTaskRequest:
            """task_idだけを指定したリクエストを返す."""
            return CompleteTaskRequest(task_id=TASK_ID)

        def test_task_idが設定される(
            self, fixture_request: CompleteTaskRequest
        ) -> None:
            """task_idが保持されることを確認する."""
            assert fixture_request.task_id == TASK_ID

        def test_completion_notesは既定でnoneになる(
            self, fixture_request: CompleteTaskRequest
        ) -> None:
            """completion_notesの既定値がNoneであることを確認する."""
            assert fixture_request.completion_notes is None

        @pytest.mark.parametrize("field_name", ["task_id", "completion_notes"])
        def test_フィールドを変更できない(
            self, fixture_request: CompleteTaskRequest, field_name: str
        ) -> None:
            """リクエストの各フィールドを再代入できないことを確認する."""
            with pytest.raises(FrozenInstanceError, match=field_name):
                setattr(
                    fixture_request, field_name, getattr(fixture_request, field_name)
                )

        def test指定したcompletion_notesが設定される(self) -> None:
            """指定したcompletion_notesが保持されることを確認する."""
            request = CompleteTaskRequest(task_id=TASK_ID, completion_notes="完了メモ")
            assert request.completion_notes == "完了メモ"

    class Test検証エラーになる:
        """不正なTask IDは生成時に拒否される."""

        @pytest.mark.parametrize("task_id", ["", "   "])
        def test_task_idが空の場合はvalue_errorになる(self, task_id: str) -> None:
            """task_idが空または空白のみの場合はValueErrorになることを確認する."""
            with pytest.raises(ValueError, match="タスク ID が必要です"):
                CompleteTaskRequest(task_id=task_id)

        def test_task_idがuuid形式でない場合はvalue_errorになる(self) -> None:
            """UUID形式でないtask_idはValueErrorになることを確認する."""
            with pytest.raises(ValueError, match="タスク ID の形式が無効です"):
                CompleteTaskRequest(task_id="not-a-uuid")

    class TestToExecutionParamsでユースケース用のパラメータに変換できる:
        """to_execution_paramsでUUIDと完了メモを変換できる."""

        @pytest.mark.parametrize("completion_notes", [None, "完了メモ"])
        def test_task_idと完了ノートをパラメータに変換できる(
            self, completion_notes: str | None
        ) -> None:
            """task_idをUUIDに変換し、完了ノートを保持することを確認する."""
            request = CompleteTaskRequest(
                task_id=TASK_ID, completion_notes=completion_notes
            )
            assert request.to_execution_params() == {
                "task_id": UUID(TASK_ID),
                "completion_notes": completion_notes,
            }


class TestCreateTaskRequest:
    """CreateTaskRequestのテスト."""

    class Test正しく生成される:
        """CreateTaskRequestが正しく生成される."""

        @pytest.fixture
        @classmethod
        def fixture_request(cls) -> CreateTaskRequest:
            """必須フィールドだけを指定したリクエストを返す."""
            return CreateTaskRequest(title="タスク", description="説明")

        def test_titleが設定される(self, fixture_request: CreateTaskRequest) -> None:
            """タイトルが保持されることを確認する."""
            assert fixture_request.title == "タスク"

        def test_descriptionが設定される(
            self, fixture_request: CreateTaskRequest
        ) -> None:
            """説明が保持されることを確認する."""
            assert fixture_request.description == "説明"

        @pytest.mark.parametrize("field_name", ["due_date", "priority", "project_id"])
        def test_任意フィールドの既定値がnoneになる(
            self, fixture_request: CreateTaskRequest, field_name: str
        ) -> None:
            """任意フィールドの既定値がNoneであることを確認する."""
            assert getattr(fixture_request, field_name) is None

        @pytest.mark.parametrize(
            "field_name", ["title", "description", "due_date", "priority", "project_id"]
        )
        def test_フィールドを変更できない(
            self, fixture_request: CreateTaskRequest, field_name: str
        ) -> None:
            """リクエストの各フィールドを再代入できないことを確認する."""
            with pytest.raises(FrozenInstanceError, match=field_name):
                setattr(
                    fixture_request, field_name, getattr(fixture_request, field_name)
                )

    class Test検証エラーになる:
        """不正な優先度やプロジェクトIDは生成時に拒否される."""

        @pytest.mark.parametrize("priority", ["", " \t", "UNKNOWN"])
        def test_無効な優先度は拒否される(self, priority: str) -> None:
            """無効な優先度は選択肢を示すValueErrorになる."""
            with pytest.raises(
                ValueError,
                match=r"^優先度は次のいずれかである必要があります: LOW, MEDIUM, HIGH$",
            ):
                CreateTaskRequest(title="タスク", description="", priority=priority)

        def test_uuid形式でないproject_idは拒否される(self) -> None:
            """UUID形式でないproject_idは生成時にValueErrorになる."""
            with pytest.raises(ValueError, match="プロジェクト ID の形式が無効です"):
                CreateTaskRequest(
                    title="タスク", description="", project_id="not-a-uuid"
                )

    class TestToExecutionParamsでパラメータに変換できる:
        """入力を正規化してユースケースのパラメータへ変換する."""

        def test_任意フィールドを省略すると必須フィールドだけが返る(self) -> None:
            """前後の空白だけを除去し、未指定のキーを含めない."""
            request = CreateTaskRequest(
                title=" \tタスク 名\u3000", description="\n 説明 文 \t"
            )
            assert request.to_execution_params() == {
                "title": "タスク 名",
                "description": "説明 文",
            }

        @pytest.mark.parametrize("description", ["", " \t\n\u3000"])
        def test_空の説明を変換できる(self, description: str) -> None:
            """空文字または空白のみの説明は空文字に変換される."""
            request = CreateTaskRequest(title="タスク", description=description)
            assert request.to_execution_params()["description"] == ""

        @pytest.mark.parametrize(
            ("priority", "expected"),
            [
                ("LOW", Priority.LOW),
                ("medium", Priority.MEDIUM),
                (" high ", Priority.HIGH),
            ],
        )
        def test_優先度を列挙型に変換できる(
            self, priority: str, expected: Priority
        ) -> None:
            """大小文字と前後の空白を正規化してPriorityに変換する."""
            request = CreateTaskRequest(
                title="タスク", description="", priority=priority
            )
            assert request.to_execution_params()["priority"] is expected

        def test_全フィールドを指定して変換できる(self) -> None:
            """期限・優先度・プロジェクトIDを適切な型に変換する."""
            due_date = datetime.now(tz=UTC) + timedelta(days=7)
            request = CreateTaskRequest(
                title="タスク",
                description="説明",
                due_date=due_date.isoformat(),
                priority="HIGH",
                project_id=PROJECT_ID,
            )
            assert request.to_execution_params() == {
                "title": "タスク",
                "description": "説明",
                "due_date": Deadline(due_date),
                "priority": Priority.HIGH,
                "project_id": UUID(PROJECT_ID),
            }

        def test_空の期限とproject_idはパラメータに含まれない(self) -> None:
            """空文字の期限とプロジェクトIDは未指定として扱われる."""
            request = CreateTaskRequest(
                title="タスク", description="", due_date="", project_id=""
            )
            assert request.to_execution_params() == {
                "title": "タスク",
                "description": "",
            }

    class Test変換時にエラーになる:
        """不正な期限やプロジェクトIDは変換時に拒否される."""

        def test_不正な日付形式は拒否される(self) -> None:
            """ISO形式でない期限はValueErrorになる."""
            request = CreateTaskRequest(
                title="タスク", description="", due_date="not-a-date"
            )
            with pytest.raises(ValueError, match="Invalid isoformat string"):
                request.to_execution_params()

        def test_タイムゾーンのない期限は拒否される(self) -> None:
            """タイムゾーンのない期限はDeadlineの検証で拒否される."""
            request = CreateTaskRequest(
                title="タスク", description="", due_date="2099-01-01T12:00:00"
            )
            with pytest.raises(ValueError, match="期限にはタイムゾーン情報が必要です"):
                request.to_execution_params()

        def test_過去の期限は拒否される(self) -> None:
            """過去の期限はDeadlineの検証で拒否される."""
            past_date = datetime.now(tz=UTC) - timedelta(days=1)
            request = CreateTaskRequest(
                title="タスク", description="", due_date=past_date.isoformat()
            )
            with pytest.raises(
                ValueError, match="期限は現在時刻以降でなければなりません"
            ):
                request.to_execution_params()


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
