# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""Taskに関連するユースケースのテスト."""

import datetime as dt
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from todo_app.application.common.result import ErrorCode
from todo_app.application.dtos.task_dto import (
    CompleteTaskRequest,
    CreateTaskRequest,
    SetTaskPriorityRequest,
    TaskResponse,
)
from todo_app.application.repositories.project_repository import ProjectRepository
from todo_app.application.repositories.task_repository import TaskRepository
from todo_app.application.service_ports.notifications import NotificationPort
from todo_app.application.use_cases.task_use_cases import (
    CompleteTaskUseCase,
    CreateTaskUseCase,
    SetTaskPriorityUseCase,
    _get_completed_at,
)
from todo_app.domain.entities.project import Project
from todo_app.domain.entities.task import Task
from todo_app.domain.exceptions import (
    BusinessRuleViolationError,
    ProjectNotFoundError,
    TaskNotFoundError,
    ValidationError,
)
from todo_app.domain.value_object import Deadline, Priority, TaskStatus

if TYPE_CHECKING:
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


class InMemoryProjectRepository(ProjectRepository):
    """テスト用のインメモリProjectリポジトリ."""

    def __init__(self) -> None:
        """空のProject保存領域と取得履歴を初期化する."""
        self._projects: dict[UUID, Project] = {}
        self.requested_project_ids: list[UUID] = []

    def get(self, project_id: UUID) -> Project:
        """IDを指定してProjectを取得する."""
        self.requested_project_ids.append(project_id)
        try:
            return self._projects[project_id]
        except KeyError as e:
            raise ProjectNotFoundError(project_id) from e

    def save(self, project: Project) -> None:
        """Projectを保存する."""
        self._projects[project.id] = project

    def delete(self, project_id: UUID) -> None:
        """Projectを削除する."""
        self._projects.pop(project_id, None)


class ValidationErrorSaveTaskRepository(InMemoryTaskRepository):
    """saveで検証エラーを送出するテスト用リポジトリ."""

    def save(self, task: Task) -> None:  # noqa: ARG002
        """Taskの保存時に検証エラーを送出する."""
        msg = "タスクを保存できません"
        raise ValidationError(msg)


class BusinessRuleViolationSaveTaskRepository(InMemoryTaskRepository):
    """saveでビジネスルール違反を送出するテスト用リポジトリ."""

    def save(self, task: Task) -> None:  # noqa: ARG002
        """Taskの保存時にビジネスルール違反を送出する."""
        msg = "タスクを保存できません"
        raise BusinessRuleViolationError(msg)


class ValidationErrorTaskRepository(InMemoryTaskRepository):
    """getで検証エラーを送出するテスト用リポジトリ."""

    def get(self, task_id: UUID) -> Task:
        """Taskの取得時に検証エラーを送出する."""
        raise ValidationError(str(task_id))


class SpyNotificationPort(NotificationPort):
    """通知の呼び出しを記録するテスト用のNotificationPort実装."""

    def __init__(self) -> None:
        """通知の記録領域を初期化する."""
        self.completed_tasks: list[Task] = []
        self.high_priority_tasks: list[Task] = []

    def notify_task_completed(self, task: Task) -> None:
        """タスク完了通知を記録する."""
        self.completed_tasks.append(task)

    def notify_task_high_priority(self, task: Task) -> None:
        """高優先度タスクの通知を記録する."""
        self.high_priority_tasks.append(task)

    def notify_task_deadline_approaching(self, task: Task, days_remaining: int) -> None:
        """期限通知を何もしない."""


class ValidationErrorTask(Task):
    """completeで検証エラーを送出するスタブTask."""

    def complete(self, notes: str | None = None) -> None:  # noqa: ARG002
        """常に検証エラーを送出する."""
        msg = "完了できないタスクです"
        raise ValidationError(msg)


class BusinessRuleViolationTask(Task):
    """状態を変更した後でビジネスルール違反を送出するスタブTask."""

    def complete(self, notes: str | None = None) -> None:
        """状態を変更してからビジネスルール違反を送出する."""
        self.status = TaskStatus.DONE
        self.completion_notes = notes
        msg = "完了できないタスクです"
        raise BusinessRuleViolationError(msg)


class NoCompletedAtTask(Task):
    """completeしてもcompleted_atを設定しないスタブTask."""

    def complete(self, notes: str | None = None) -> None:
        """completed_atを設定せずに完了状態へ遷移する."""
        self.status = TaskStatus.DONE
        self.completion_notes = notes


class TestCreateTaskUseCase:
    """CreateTaskUseCaseのテスト."""

    @pytest.fixture
    @classmethod
    def fixture_task_repository(cls) -> InMemoryTaskRepository:
        """テスト用のTaskリポジトリを返す."""
        return InMemoryTaskRepository()

    @pytest.fixture
    @classmethod
    def fixture_project_repository(cls) -> InMemoryProjectRepository:
        """テスト用のProjectリポジトリを返す."""
        return InMemoryProjectRepository()

    class Test有効なリクエストで作成できる:
        """有効なリクエストでTaskが作成・保存される."""

        @pytest.fixture
        @classmethod
        def fixture_task_repository(cls) -> InMemoryTaskRepository:
            """空のTaskリポジトリを返す."""
            return InMemoryTaskRepository()

        @pytest.fixture
        @classmethod
        def fixture_result(
            cls,
            fixture_task_repository: InMemoryTaskRepository,
            fixture_project_repository: InMemoryProjectRepository,
        ) -> Result:
            """ProjectなしのTask作成を実行した結果を返す."""
            request = CreateTaskRequest(
                title="  テストタスク  ",
                description="  タスクの説明  ",
            )
            return CreateTaskUseCase(
                fixture_task_repository, fixture_project_repository
            ).execute(request)

        @pytest.fixture
        @classmethod
        def fixture_task(
            cls,
            fixture_result: Result,
            fixture_task_repository: InMemoryTaskRepository,
        ) -> Task:
            """作成に成功して保存されたTaskを返す."""
            assert fixture_result.is_success is True
            (task,) = fixture_task_repository.saved_tasks
            return task

        def test_taskが初期値と整形済みの情報で保存される(
            self, fixture_task: Task
        ) -> None:
            """Taskの情報が整形され、既定値とともに保存されることを確認する."""
            assert (
                fixture_task.title,
                fixture_task.description,
                fixture_task.priority,
                fixture_task.due_date,
                fixture_task.status,
            ) == (
                "テストタスク",
                "タスクの説明",
                Priority.MEDIUM,
                None,
                TaskStatus.TODO,
            )

        def test_指定した期限がtaskに設定される(
            self,
            fixture_task_repository: InMemoryTaskRepository,
            fixture_project_repository: InMemoryProjectRepository,
        ) -> None:
            """リクエストで指定した期限がTaskに設定されることを確認する."""
            due_date = dt.datetime.fromisoformat("2026-12-01T10:00:00+09:00")
            request = CreateTaskRequest(
                title="テストタスク",
                description="タスクの説明",
                due_date=due_date.isoformat(),
            )
            CreateTaskUseCase(
                fixture_task_repository, fixture_project_repository
            ).execute(request)
            (task,) = fixture_task_repository.saved_tasks
            assert task.due_date == Deadline(due_date)

    class TestProjectに紐づけて作成できる:
        """指定されたProjectにTaskを紐づけて作成する."""

        @pytest.fixture
        @classmethod
        def fixture_project(cls) -> Project:
            """Taskに紐づけるProjectを返す."""
            return Project(name="テストプロジェクト")

        @pytest.fixture
        @classmethod
        def fixture_project_repository(
            cls, fixture_project: Project
        ) -> InMemoryProjectRepository:
            """Projectを1件保存したリポジトリを返す."""
            repository = InMemoryProjectRepository()
            repository.save(fixture_project)
            return repository

        @pytest.fixture
        @classmethod
        def fixture_task_repository(cls) -> InMemoryTaskRepository:
            """空のTaskリポジトリを返す."""
            return InMemoryTaskRepository()

        @pytest.fixture
        @classmethod
        def fixture_task(
            cls,
            fixture_project: Project,
            fixture_project_repository: InMemoryProjectRepository,
            fixture_task_repository: InMemoryTaskRepository,
        ) -> Task:
            """Projectに紐づけて作成されたTaskを返す."""
            request = CreateTaskRequest(
                title="テストタスク",
                description="タスクの説明",
                project_id=str(fixture_project.id),
            )
            result = CreateTaskUseCase(
                fixture_task_repository, fixture_project_repository
            ).execute(request)
            assert result.is_success is True
            (task,) = fixture_task_repository.saved_tasks
            return task

        def test_taskにproject_idが設定される(
            self, fixture_task: Task, fixture_project: Project
        ) -> None:
            """作成したTaskに指定されたProject IDが設定されることを確認する."""
            assert fixture_task.project_id == fixture_project.id

    class Test存在しないprojectの場合は失敗する:
        """存在しないProjectを指定した場合は失敗結果を返す."""

        @pytest.fixture
        @classmethod
        def fixture_project_id(cls) -> UUID:
            """存在しないProjectのIDを返す."""
            return uuid4()

        @pytest.fixture
        @classmethod
        def fixture_result(
            cls,
            fixture_task_repository: InMemoryTaskRepository,
            fixture_project_repository: InMemoryProjectRepository,
            fixture_project_id: UUID,
        ) -> Result:
            """存在しないProjectを指定してTask作成を実行した結果を返す."""
            request = CreateTaskRequest(
                title="テストタスク",
                description="タスクの説明",
                project_id=str(fixture_project_id),
            )
            return CreateTaskUseCase(
                fixture_task_repository, fixture_project_repository
            ).execute(request)

        @pytest.fixture
        @classmethod
        def fixture_error(cls, fixture_result: Result) -> Error:
            """失敗結果からエラーを取り出す."""
            error = fixture_result.error
            assert error is not None
            return error

        def test_errorのcodeがnot_foundになる(self, fixture_error: Error) -> None:
            """Project未検出時にnot_foundエラーが返ることを確認する."""
            assert fixture_error.code is ErrorCode.NOT_FOUND

    class TestValidationErrorの場合は失敗する:
        """Task保存時の検証エラーを失敗結果に変換する."""

        @pytest.fixture
        @classmethod
        def fixture_result(
            cls, fixture_project_repository: InMemoryProjectRepository
        ) -> Result:
            """検証エラーが発生したTask作成の結果を返す."""
            request = CreateTaskRequest(title="テストタスク", description="")
            return CreateTaskUseCase(
                ValidationErrorSaveTaskRepository(), fixture_project_repository
            ).execute(request)

        @pytest.fixture
        @classmethod
        def fixture_error(cls, fixture_result: Result) -> Error:
            """失敗結果からエラーを取り出す."""
            error = fixture_result.error
            assert error is not None
            return error

        def test_validation_errorに変換される(self, fixture_error: Error) -> None:
            """検証エラーがvalidation_errorに変換されることを確認する."""
            assert (fixture_error.code, fixture_error.message) == (
                ErrorCode.VALIDATION_ERROR,
                "タスクを保存できません",
            )

    class TestBusinessRuleViolationErrorの場合は失敗する:
        """Task保存時のビジネスルール違反を失敗結果に変換する."""

        @pytest.fixture
        @classmethod
        def fixture_result(
            cls, fixture_project_repository: InMemoryProjectRepository
        ) -> Result:
            """ビジネスルール違反が発生したTask作成の結果を返す."""
            request = CreateTaskRequest(title="テストタスク", description="")
            return CreateTaskUseCase(
                BusinessRuleViolationSaveTaskRepository(), fixture_project_repository
            ).execute(request)

        @pytest.fixture
        @classmethod
        def fixture_error(cls, fixture_result: Result) -> Error:
            """失敗結果からエラーを取り出す."""
            error = fixture_result.error
            assert error is not None
            return error

        def test_business_rule_violationに変換される(
            self, fixture_error: Error
        ) -> None:
            """ビジネスルール違反が対応するエラーに変換されることを確認する."""
            assert (fixture_error.code, fixture_error.message) == (
                ErrorCode.BUSINESS_RULE_VIOLATION,
                "タスクを保存できません",
            )


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
        def fixture_notification_service(cls) -> SpyNotificationPort:
            """通知の呼び出しを記録する."""
            return SpyNotificationPort()

        @pytest.fixture
        @classmethod
        def fixture_result(
            cls,
            fixture_repository: InMemoryTaskRepository,
            fixture_task: Task,
            fixture_notification_service: SpyNotificationPort,
        ) -> Result:
            """ユースケースを実行した結果を返すフィクスチャ."""
            use_case = CompleteTaskUseCase(
                task_repository=fixture_repository,
                notification_service=fixture_notification_service,
            )
            request = CompleteTaskRequest(
                task_id=str(fixture_task.id), completion_notes="完了メモ"
            )
            return use_case.execute(request)

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
            """valueにTaskResponseが設定されTaskのidが文字列であることを確認する."""
            assert fixture_result.value.id == str(fixture_task.id)

        def test_valueのstatusがcompletedになる(self, fixture_result: Result) -> None:
            """valueのstatusがDONEになることを確認する."""
            assert fixture_result.value.status is TaskStatus.DONE

        def test_valueのcompletion_dateが完了時刻のisoformatになる(
            self, fixture_result: Result, fixture_completed_at: dt.datetime
        ) -> None:
            """valueのcompletion_dateに完了時刻が設定されることを確認する."""
            assert fixture_result.value.completion_date == fixture_completed_at

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

        def test_task完了通知が送信される(
            self,
            fixture_notification_service: SpyNotificationPort,
            fixture_completed_task: Task,
        ) -> None:
            """完了したTaskが通知サービスに渡されることを確認する."""
            assert fixture_notification_service.completed_tasks == [
                fixture_completed_task
            ]

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
            use_case = CompleteTaskUseCase(
                task_repository=repository,
                notification_service=SpyNotificationPort(),
            )
            return use_case.execute(CompleteTaskRequest(task_id=str(fixture_task.id)))

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
            use_case = CompleteTaskUseCase(
                task_repository=InMemoryTaskRepository(),
                notification_service=SpyNotificationPort(),
            )
            return use_case.execute(CompleteTaskRequest(task_id=str(fixture_task_id)))

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
            use_case = CompleteTaskUseCase(
                task_repository=repository,
                notification_service=SpyNotificationPort(),
            )
            return use_case.execute(CompleteTaskRequest(task_id=str(task.id)))

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

    class Testビジネスルール違反の場合は失敗して状態が復元される:
        """BusinessRuleViolationErrorを結果に変換し、Taskを元の状態に戻す."""

        @pytest.fixture
        @classmethod
        def fixture_repository(cls) -> InMemoryTaskRepository:
            """空のTaskリポジトリを返す."""
            return InMemoryTaskRepository()

        @pytest.fixture
        @classmethod
        def fixture_task(cls, fixture_repository: InMemoryTaskRepository) -> Task:
            """ビジネスルール違反を送出するTaskを保存する."""
            task = BusinessRuleViolationTask(
                title="Test Task", description="Test Description"
            )
            fixture_repository.save(task)
            fixture_repository.saved_tasks.clear()
            return task

        @pytest.fixture
        @classmethod
        def fixture_result(
            cls,
            fixture_repository: InMemoryTaskRepository,
            fixture_task: Task,
        ) -> Result:
            """ビジネスルール違反となる実行結果を返す."""
            use_case = CompleteTaskUseCase(
                task_repository=fixture_repository,
                notification_service=SpyNotificationPort(),
            )
            request = CompleteTaskRequest(task_id=str(fixture_task.id))
            return use_case.execute(request)

        @pytest.fixture
        @classmethod
        def fixture_error(cls, fixture_result: Result) -> Error:
            """実行結果からerrorを取り出す."""
            error = fixture_result.error
            assert error is not None
            return error

        def test_errorのcodeがbusiness_rule_violationになる(
            self, fixture_error: Error
        ) -> None:
            """errorのcodeがBUSINESS_RULE_VIOLATIONになることを確認する."""
            assert fixture_error.code is ErrorCode.BUSINESS_RULE_VIOLATION

        def test_errorのmessageに例外のメッセージが設定される(
            self, fixture_error: Error
        ) -> None:
            """errorのmessageが例外のメッセージになることを確認する."""
            assert fixture_error.message == "完了できないタスクです"

        def test_repositoryのtask状態が実行前に復元される(
            self,
            fixture_repository: InMemoryTaskRepository,
            fixture_task: Task,
        ) -> None:
            """例外送出前の変更を破棄し、保存済み状態を復元する."""
            task = fixture_repository.get(fixture_task.id)
            assert (task.status, task.completion_notes) == (TaskStatus.TODO, None)

    class TestCompletedAtが設定されない場合も完了レスポンスになる:
        """completed_atがNoneでもTaskResponseに反映される."""

        @pytest.fixture
        @classmethod
        def fixture_result(cls) -> Result:
            """completed_atを設定しないTaskでユースケースを実行した結果を返す."""
            repository = InMemoryTaskRepository()
            task = NoCompletedAtTask(title="Test Task", description="Test Description")
            repository.save(task)
            use_case = CompleteTaskUseCase(
                task_repository=repository,
                notification_service=SpyNotificationPort(),
            )
            request = CompleteTaskRequest(task_id=str(task.id))
            return use_case.execute(request)

        def test_実行が成功する(self, fixture_result: Result) -> None:
            """completed_atがNoneでも実行が成功することを確認する."""
            assert fixture_result.is_success is True

        def test_completion_dateはnoneになる(self, fixture_result: Result) -> None:
            """completed_atがNoneの場合はレスポンスのcompletion_dateもNoneになる."""
            assert fixture_result.value.completion_date is None


class TestGetCompletedAt:
    """_get_completed_atのテスト."""

    def test_completed_atが設定されているtaskから取得できる(self) -> None:
        """Taskに設定された完了時刻を返すことを確認する."""
        completed_at = dt.datetime.now(tz=dt.UTC)
        task = Task(title="Test Task", description="Test Description")
        task.completed_at = completed_at
        assert _get_completed_at(task) is completed_at

    def test_completed_atがnoneの場合はvalue_errorになる(self) -> None:
        """completed_atがNoneの場合にValueErrorになることを確認する."""
        task = Task(title="Test Task", description="Test Description")
        with pytest.raises(
            ValueError, match="完了したTaskにcompleted_atが設定されていません。"
        ):
            _get_completed_at(task)


class TestSetTaskPriorityUseCase:
    """SetTaskPriorityUseCaseのテスト."""

    class Test高優先度を設定すると通知される:
        """高優先度を設定してTaskを保存し、通知する."""

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
        def fixture_notification_port(cls) -> SpyNotificationPort:
            """通知の呼び出しを記録するフィクスチャ."""
            return SpyNotificationPort()

        @pytest.fixture
        @classmethod
        def fixture_result(
            cls,
            fixture_repository: InMemoryTaskRepository,
            fixture_task: Task,
            fixture_notification_port: SpyNotificationPort,
        ) -> Result:
            """高優先度への変更を実行した結果を返す."""
            use_case = SetTaskPriorityUseCase(
                task_repository=fixture_repository,
                notification_service=fixture_notification_port,
            )
            request = SetTaskPriorityRequest(
                task_id=str(fixture_task.id), priority="HIGH"
            )
            return use_case.execute(request)

        def test_実行が成功する(self, fixture_result: Result) -> None:
            """ユースケースの実行が成功することを確認する."""
            assert fixture_result.is_success is True

        def test_taskの優先度が更新される(
            self, fixture_task: Task, fixture_result: Result
        ) -> None:
            """Taskの優先度がHIGHに更新されることを確認する."""
            assert (
                fixture_result.is_success,
                fixture_task.priority,
            ) == (True, Priority.HIGH)

        def test_taskがリポジトリに保存される(
            self,
            fixture_repository: InMemoryTaskRepository,
            fixture_task: Task,
            fixture_result: Result,
        ) -> None:
            """更新されたTaskがリポジトリに保存されることを確認する."""
            assert (fixture_result.is_success, fixture_repository.saved_tasks) == (
                True,
                [fixture_task],
            )

        def test高優先度の通知が送信される(
            self,
            fixture_notification_port: SpyNotificationPort,
            fixture_task: Task,
            fixture_result: Result,
        ) -> None:
            """高優先度を設定したTaskの通知が送信されることを確認する."""
            assert (
                fixture_result.is_success,
                fixture_notification_port.high_priority_tasks,
            ) == (True, [fixture_task])

        def test_task_responseが返される(
            self, fixture_result: Result, fixture_task: Task
        ) -> None:
            """成功値に更新後のTaskResponseが含まれることを確認する."""
            assert fixture_result.value == TaskResponse.from_entity(fixture_task)

    class Test高優先度以外では通知されない:
        """高優先度以外に設定した場合は通知しない."""

        @pytest.mark.parametrize(
            ("priority", "expected_priority"),
            [("LOW", Priority.LOW), ("MEDIUM", Priority.MEDIUM)],
        )
        def test_優先度が更新され通知されない(
            self, priority: str, expected_priority: Priority
        ) -> None:
            """高優先度以外への変更は保存され、通知されないことを確認する."""
            repository = InMemoryTaskRepository()
            task = Task(title="Test Task", description="Test Description")
            repository.save(task)
            repository.saved_tasks.clear()
            notification_port = SpyNotificationPort()
            use_case = SetTaskPriorityUseCase(repository, notification_port)

            result = use_case.execute(
                SetTaskPriorityRequest(task_id=str(task.id), priority=priority)
            )

            assert (
                result.is_success,
                task.priority,
                repository.saved_tasks,
                notification_port.high_priority_tasks,
            ) == (True, expected_priority, [task], [])

    class Test存在しないtaskの場合は失敗する:
        """存在しないTaskを指定した場合は失敗結果が返る."""

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_task_id(cls) -> UUID:
            """存在しないTaskのidを生成する."""
            return uuid4()

        @pytest.fixture
        @classmethod
        def fixture_result(cls, fixture_task_id: UUID) -> Result:
            """空のリポジトリでユースケースを実行した結果を返す."""
            use_case = SetTaskPriorityUseCase(
                task_repository=InMemoryTaskRepository(),
                notification_service=SpyNotificationPort(),
            )
            request = SetTaskPriorityRequest(
                task_id=str(fixture_task_id), priority="HIGH"
            )
            return use_case.execute(request)

        @pytest.fixture
        @classmethod
        def fixture_error(cls, fixture_result: Result) -> Error:
            """実行結果からerrorを取り出す."""
            error = fixture_result.error
            assert error is not None
            return error

        def test_実行が失敗する(self, fixture_result: Result) -> None:
            """ユースケースの実行が失敗することを確認する."""
            assert fixture_result.is_success is False

        def test_errorのcodeがnot_foundになる(self, fixture_error: Error) -> None:
            """Error codeがNOT_FOUNDになることを確認する."""
            assert fixture_error.code is ErrorCode.NOT_FOUND

        def test_errorのmessageにtask_idが含まれる(
            self, fixture_error: Error, fixture_task_id: UUID
        ) -> None:
            """Error messageにTaskのidが含まれることを確認する."""
            assert str(fixture_task_id) in fixture_error.message

    class Test検証エラーの場合は失敗する:
        """リポジトリが検証エラーを送出した場合は失敗結果が返る."""

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_task_id(cls) -> UUID:
            """テスト用のTask IDを生成する."""
            return uuid4()

        @pytest.fixture
        @classmethod
        def fixture_result(cls, fixture_task_id: UUID) -> Result:
            """検証エラーを送出するリポジトリで実行した結果を返す."""
            use_case = SetTaskPriorityUseCase(
                task_repository=ValidationErrorTaskRepository(),
                notification_service=SpyNotificationPort(),
            )
            request = SetTaskPriorityRequest(
                task_id=str(fixture_task_id), priority="HIGH"
            )
            return use_case.execute(request)

        @pytest.fixture
        @classmethod
        def fixture_error(cls, fixture_result: Result) -> Error:
            """実行結果からerrorを取り出す."""
            error = fixture_result.error
            assert error is not None
            return error

        def test_実行が失敗する(self, fixture_result: Result) -> None:
            """ユースケースの実行が失敗することを確認する."""
            assert fixture_result.is_success is False

        def test_errorのcodeがvalidation_errorになる(
            self, fixture_error: Error
        ) -> None:
            """Error codeがVALIDATION_ERRORになることを確認する."""
            assert fixture_error.code is ErrorCode.VALIDATION_ERROR

        def test_errorのmessageが保持される(
            self, fixture_error: Error, fixture_task_id: UUID
        ) -> None:
            """例外のメッセージがErrorに保持されることを確認する."""
            assert fixture_error.message == str(fixture_task_id)
