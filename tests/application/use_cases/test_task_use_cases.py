# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""CompleteTaskUseCaseのテスト."""

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from todo_app.application.common.result import ErrorCode
from todo_app.application.repositories.task_repository import TaskRepository
from todo_app.application.use_cases.task_use_cases import CompleteTaskUseCase
from todo_app.domain.entities.task import Task
from todo_app.domain.exceptions import TaskNotFoundError, ValidationError
from todo_app.domain.value_object import TaskStatus

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import Sequence
    from uuid import UUID

    from todo_app.application.common.result import Error, Result


class InMemoryTaskRepository(TaskRepository):
    """テスト用のインメモリTaskリポジトリ."""

    def __init__(self) -> None:
        """空のTask保存領域と保存履歴を初期化する."""
        self._tasks: dict[UUID, Task] = {}
        self.saved_tasks: list[Task] = []

    def get(self, task_id: UUID) -> Task:
        """IDを指定してTaskを取得する."""
        try:
            return self._tasks[task_id]
        except KeyError as e:
            raise TaskNotFoundError(task_id) from e

    def save(self, task: Task) -> None:
        """Taskを保存し、保存履歴に記録する."""
        self._tasks[task.id] = task
        self.saved_tasks.append(task)

    def delete(self, task_id: UUID) -> None:
        """Taskを削除する."""
        self._tasks.pop(task_id, None)

    def find_by_project(self, project_id: UUID) -> Sequence[Task]:
        """Projectに属するTaskを検索する."""
        return [t for t in self._tasks.values() if t.project_id == project_id]

    def get_active_tasks(self) -> Sequence[Task]:
        """アクティブなTaskを取得する."""
        return [t for t in self._tasks.values() if t.status is not TaskStatus.DONE]


class ValidationErrorTask(Task):
    """completeで検証エラーを送出するスタブTask."""

    def complete(self, notes: str | None = None) -> None:  # noqa: ARG002
        """常に検証エラーを送出する."""
        msg = "完了できないタスクです"
        raise ValidationError(msg)


class NoCompletedAtTask(Task):
    """completeしてもcompleted_atを設定しないスタブTask."""

    def complete(self, notes: str | None = None) -> None:
        """completed_atを設定せずに完了状態へ遷移する."""
        self.status = TaskStatus.DONE
        self.completion_notes = notes


class TestCompleteTaskUseCase:
    """CompleteTaskUseCaseのテスト."""

    class TestNotesを指定して完了できる:
        """notesを指定してTaskを完了できる."""

        @pytest.fixture
        @classmethod
        def fixture_repository(cls) -> InMemoryTaskRepository:
            """テスト用のリポジトリを生成するフィクスチャ."""
            return InMemoryTaskRepository()

        @pytest.fixture
        @classmethod
        def fixture_task(cls, fixture_repository: InMemoryTaskRepository) -> Task:
            """リポジトリに保存済みのTaskを生成するフィクスチャ."""
            task = Task(title="Test Task", description="Test Description")
            fixture_repository.save(task)
            fixture_repository.saved_tasks.clear()
            return task

        @pytest.fixture
        @classmethod
        def fixture_result(
            cls, fixture_repository: InMemoryTaskRepository, fixture_task: Task
        ) -> Result:
            """ユースケースを実行した結果を返すフィクスチャ."""
            use_case = CompleteTaskUseCase(task_repository=fixture_repository)
            return use_case.execute(fixture_task.id, completion_notes="完了メモ")

        @pytest.fixture
        @classmethod
        def fixture_completed_task(
            cls, fixture_result: Result, fixture_task: Task
        ) -> Task:
            """ユースケースの実行成功後のTaskを返すフィクスチャ."""
            assert fixture_result.is_success is True
            return fixture_task

        @pytest.fixture
        @classmethod
        def fixture_completed_at(cls, fixture_completed_task: Task) -> dt.datetime:
            """実行後のTaskに記録された完了時刻を返すフィクスチャ."""
            completed_at = fixture_completed_task.completed_at
            assert completed_at is not None
            return completed_at

        def test_実行が成功する(self, fixture_result: Result) -> None:
            """ユースケースの実行が成功することを確認する."""
            assert fixture_result.is_success is True

        def test_valueにtaskのidが設定される(
            self, fixture_result: Result, fixture_task: Task
        ) -> None:
            """valueにTaskのidが文字列で設定されることを確認する."""
            assert fixture_result.value["id"] == str(fixture_task.id)

        def test_valueのstatusがcompletedになる(self, fixture_result: Result) -> None:
            """valueのstatusがcompletedになることを確認する."""
            assert fixture_result.value["status"] == "completed"

        def test_valueのcompletion_dateが完了時刻のisoformatになる(
            self, fixture_result: Result, fixture_completed_at: dt.datetime
        ) -> None:
            """valueのcompletion_dateが完了時刻のisoformatになることを確認する."""
            assert (
                fixture_result.value["completion_date"]
                == fixture_completed_at.isoformat()
            )

        def test_taskのstatusがdoneになる(self, fixture_completed_task: Task) -> None:
            """TaskのstatusがDONEになることを確認する."""
            assert fixture_completed_task.status is TaskStatus.DONE

        def test_taskのcompletion_notesが設定される(
            self, fixture_completed_task: Task
        ) -> None:
            """Taskのcompletion_notesに指定したnotesが設定されることを確認する."""
            assert fixture_completed_task.completion_notes == "完了メモ"

        def test_taskがリポジトリに保存される(
            self,
            fixture_repository: InMemoryTaskRepository,
            fixture_completed_task: Task,
        ) -> None:
            """完了したTaskがリポジトリに保存されることを確認する."""
            assert fixture_repository.saved_tasks == [fixture_completed_task]

    class TestNotesを指定せずに完了できる:
        """notesを指定せずにTaskを完了できる."""

        @pytest.fixture
        @classmethod
        def fixture_task(cls) -> Task:
            """テスト用のTaskを生成するフィクスチャ."""
            return Task(title="Test Task", description="Test Description")

        @pytest.fixture
        @classmethod
        def fixture_result(cls, fixture_task: Task) -> Result:
            """notesを指定せずにユースケースを実行した結果を返すフィクスチャ."""
            repository = InMemoryTaskRepository()
            repository.save(fixture_task)
            use_case = CompleteTaskUseCase(task_repository=repository)
            return use_case.execute(fixture_task.id)

        @pytest.fixture
        @classmethod
        def fixture_completed_task(
            cls, fixture_result: Result, fixture_task: Task
        ) -> Task:
            """ユースケースの実行成功後のTaskを返すフィクスチャ."""
            assert fixture_result.is_success is True
            return fixture_task

        def test_実行が成功する(self, fixture_result: Result) -> None:
            """ユースケースの実行が成功することを確認する."""
            assert fixture_result.is_success is True

        def test_completion_notesはnoneのまま(
            self, fixture_completed_task: Task
        ) -> None:
            """Taskのcompletion_notesがNoneのままであることを確認する."""
            assert fixture_completed_task.completion_notes is None

    class Test存在しないtaskの場合は失敗する:
        """存在しないTaskを指定した場合は失敗結果が返る."""

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_task_id(cls) -> UUID:
            """存在しないTaskのidを生成するフィクスチャ."""
            return uuid4()

        @pytest.fixture
        @classmethod
        def fixture_result(cls, fixture_task_id: UUID) -> Result:
            """空のリポジトリでユースケースを実行した結果を返すフィクスチャ."""
            use_case = CompleteTaskUseCase(task_repository=InMemoryTaskRepository())
            return use_case.execute(fixture_task_id)

        @pytest.fixture
        @classmethod
        def fixture_error(cls, fixture_result: Result) -> Error:
            """実行結果からerrorを取り出すフィクスチャ."""
            error = fixture_result.error
            assert error is not None
            return error

        def test_実行が失敗する(self, fixture_result: Result) -> None:
            """ユースケースの実行が失敗することを確認する."""
            assert fixture_result.is_success is False

        def test_errorのcodeがnot_foundになる(self, fixture_error: Error) -> None:
            """errorのcodeがNOT_FOUNDになることを確認する."""
            assert fixture_error.code is ErrorCode.NOT_FOUND

        def test_errorのmessageにtask_idが含まれる(
            self, fixture_error: Error, fixture_task_id: UUID
        ) -> None:
            """errorのmessageにTaskのidが含まれることを確認する."""
            assert str(fixture_task_id) in fixture_error.message

    class Test検証エラーの場合は失敗する:
        """completeが検証エラーを送出した場合は失敗結果が返る."""

        @pytest.fixture
        @classmethod
        def fixture_result(cls) -> Result:
            """検証エラーを送出するTaskでユースケースを実行した結果を返すフィクスチャ."""
            repository = InMemoryTaskRepository()
            task = ValidationErrorTask(
                title="Test Task", description="Test Description"
            )
            repository.save(task)
            use_case = CompleteTaskUseCase(task_repository=repository)
            return use_case.execute(task.id)

        @pytest.fixture
        @classmethod
        def fixture_error(cls, fixture_result: Result) -> Error:
            """実行結果からerrorを取り出すフィクスチャ."""
            error = fixture_result.error
            assert error is not None
            return error

        def test_実行が失敗する(self, fixture_result: Result) -> None:
            """ユースケースの実行が失敗することを確認する."""
            assert fixture_result.is_success is False

        def test_errorのcodeがvalidation_errorになる(
            self, fixture_error: Error
        ) -> None:
            """errorのcodeがVALIDATION_ERRORになることを確認する."""
            assert fixture_error.code is ErrorCode.VALIDATION_ERROR

        def test_errorのmessageに例外のメッセージが設定される(
            self, fixture_error: Error
        ) -> None:
            """errorのmessageに例外のメッセージが設定されることを確認する."""
            assert fixture_error.message == "完了できないタスクです"

    class TestCompletedAtが設定されない場合は例外になる:
        """completeがcompleted_atを設定しない場合はValueErrorが送出される."""

        def test_value_errorが送出される(self) -> None:
            """completed_atがNoneのままの場合にValueErrorが送出されることを確認する."""
            repository = InMemoryTaskRepository()
            task = NoCompletedAtTask(title="Test Task", description="Test Description")
            repository.save(task)
            use_case = CompleteTaskUseCase(task_repository=repository)
            with pytest.raises(
                ValueError, match="完了したTaskにcompleted_atが設定されていません。"
            ):
                use_case.execute(task.id)
