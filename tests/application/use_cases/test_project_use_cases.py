# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""Projectに関連するユースケースのテスト."""

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from todo_app.application.common.result import ErrorCode
from todo_app.application.dtos.project_dto import (
    CompleteProjectRequest,
    CompleteProjectResponse,
    CreateProjectRequest,
    ProjectResponse,
)
from todo_app.application.repositories.project_repository import ProjectRepository
from todo_app.application.repositories.task_repository import TaskRepository
from todo_app.application.service_ports.notifications import NotificationPort
from todo_app.application.use_cases.project_use_cases import (
    CompleteProjectUseCase,
    CreateProjectUseCase,
)
from todo_app.domain.entities.project import (
    DESCRIPTION_MAX_LENGTH,
    NAME_MAX_LENGTH,
    Project,
)
from todo_app.domain.entities.task import Task
from todo_app.domain.exceptions import (
    BusinessRuleViolationError,
    ProjectNotFoundError,
    TaskNotFoundError,
    ValidationError,
)
from todo_app.domain.value_object import ProjectStatus, TaskStatus

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import Sequence
    from uuid import UUID

    from todo_app.application.common.result import Error, Result


class InMemoryProjectRepository(ProjectRepository):
    """テスト用のインメモリProjectリポジトリ."""

    def __init__(self) -> None:
        """空のProject保存領域と保存履歴を初期化する."""
        self._projects: dict[UUID, Project] = {}
        self.saved_projects: list[Project] = []

    def get(self, project_id: UUID) -> Project:
        """IDを指定してProjectを取得する."""
        try:
            return self._projects[project_id]
        except KeyError as e:
            raise ProjectNotFoundError(project_id) from e

    def save(self, project: Project) -> None:
        """Projectを保存し、保存履歴に記録する."""
        self._projects[project.id] = project
        self.saved_projects.append(project)

    def delete(self, project_id: UUID) -> None:
        """Projectを削除する."""
        self._projects.pop(project_id, None)


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


class SpyNotificationPort(NotificationPort):
    """通知の呼び出しを記録するテスト用のNotificationPort実装."""

    def __init__(self) -> None:
        """通知の記録領域を初期化する."""
        self.completed_tasks: list[Task] = []
        self.high_priority_tasks: list[Task] = []
        self.deadline_notifications: list[tuple[Task, int]] = []

    def notify_task_completed(self, task: Task) -> None:
        """タスク完了の通知を記録する."""
        self.completed_tasks.append(task)

    def notify_task_high_priority(self, task: Task) -> None:
        """高優先度タスクの通知を記録する."""
        self.high_priority_tasks.append(task)

    def notify_task_deadline_approaching(self, task: Task, days_remaining: int) -> None:
        """締め切りが近づいたタスクの通知を記録する."""
        self.deadline_notifications.append((task, days_remaining))


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


class BusinessRuleViolationProjectRepository(InMemoryProjectRepository):
    """保存時にビジネスルール違反を送出するリポジトリ."""

    def save(self, project: Project) -> None:
        """指定されたプロジェクトの保存を拒否する."""
        msg = f"{project.name}は作成できません"
        raise BusinessRuleViolationError(msg)


class TestCreateProjectUseCase:
    """CreateProjectUseCaseのテスト."""

    @pytest.fixture
    @classmethod
    def fixture_repository(cls) -> InMemoryProjectRepository:
        """テスト用の空のリポジトリを返す."""
        return InMemoryProjectRepository()

    @pytest.fixture
    @classmethod
    def fixture_error(cls, fixture_result: Result) -> Error:
        """失敗結果からエラーを取り出す."""
        error = fixture_result.error
        assert error is not None
        return error

    class Testプロジェクトを作成できる:
        """リクエストからプロジェクトを作成して保存する."""

        @pytest.fixture(
            params=[
                CreateProjectRequest(name="テストプロジェクト"),
                CreateProjectRequest(
                    name="テストプロジェクト", description="プロジェクトの説明"
                ),
                CreateProjectRequest(
                    name=" \tテストプロジェクト\u3000",
                    description="\n プロジェクトの説明 \t",
                ),
            ]
        )
        @classmethod
        def fixture_request(
            cls, request: pytest.FixtureRequest
        ) -> CreateProjectRequest:
            """説明の省略・指定・前後の空白を含むリクエストを返す."""
            return request.param

        @pytest.fixture
        @classmethod
        def fixture_result(
            cls,
            fixture_repository: InMemoryProjectRepository,
            fixture_request: CreateProjectRequest,
        ) -> Result:
            """プロジェクト作成を実行した結果を返す."""
            return CreateProjectUseCase(fixture_repository).execute(fixture_request)

        @pytest.fixture
        @classmethod
        def fixture_project(
            cls, fixture_result: Result, fixture_repository: InMemoryProjectRepository
        ) -> Project:
            """作成に成功して一度だけ保存されたプロジェクトを返す."""
            assert fixture_result.is_success is True
            (project,) = fixture_repository.saved_projects
            return project

        @pytest.fixture
        @classmethod
        def fixture_response(cls, fixture_result: Result) -> ProjectResponse:
            """成功値からProjectResponseを取り出す."""
            response = fixture_result.value
            assert isinstance(response, ProjectResponse)
            return response

        def test_実行が成功する(self, fixture_result: Result) -> None:
            """作成が成功することを確認する."""
            assert fixture_result.is_success is True

        def test_名前が空白除去後に保存される(self, fixture_project: Project) -> None:
            """前後の空白を除去した名前で保存されることを確認する."""
            assert fixture_project.name == "テストプロジェクト"

        def test_説明が空白除去後に保存される(
            self, fixture_project: Project, fixture_request: CreateProjectRequest
        ) -> None:
            """説明が指定または省略されたとおりに保存されることを確認する."""
            assert fixture_project.description == fixture_request.description.strip()

        def test_保存したプロジェクトをidで取得できる(
            self,
            fixture_project: Project,
            fixture_repository: InMemoryProjectRepository,
        ) -> None:
            """作成したプロジェクトがリポジトリに永続化されることを確認する."""
            assert fixture_repository.get(fixture_project.id) is fixture_project

        def test_作成したプロジェクトのレスポンスが返る(
            self, fixture_response: ProjectResponse, fixture_project: Project
        ) -> None:
            """保存したプロジェクトに対応するレスポンスが返ることを確認する."""
            assert fixture_response == ProjectResponse.from_entity(fixture_project)

        def test_作成時の状態がactiveになる(
            self, fixture_response: ProjectResponse
        ) -> None:
            """作成時のレスポンスがACTIVE状態であることを確認する."""
            assert fixture_response.status == "ACTIVE"

        def test_作成時の完了日時はnoneになる(
            self, fixture_response: ProjectResponse
        ) -> None:
            """作成時の完了日時が未設定であることを確認する."""
            assert fixture_response.completion_date is None

        def test_作成時のタスク一覧は空になる(
            self, fixture_response: ProjectResponse
        ) -> None:
            """作成時のタスク一覧が空であることを確認する."""
            assert fixture_response.tasks == []

    class Test検証エラーの場合は失敗する:
        """不正な入力では保存せずに検証エラーを返す."""

        @pytest.fixture(
            params=[
                (
                    CreateProjectRequest(name=" \t\u3000"),
                    "プロジェクト名が必要です",
                ),
                (
                    CreateProjectRequest(name="名" * (NAME_MAX_LENGTH + 1)),
                    f"プロジェクト名は{NAME_MAX_LENGTH}文字以下としてください",
                ),
                (
                    CreateProjectRequest(
                        name="テストプロジェクト",
                        description="説" * (DESCRIPTION_MAX_LENGTH + 1),
                    ),
                    f"説明は{DESCRIPTION_MAX_LENGTH}文字以下としてください",
                ),
            ]
        )
        @classmethod
        def fixture_invalid_input(
            cls, request: pytest.FixtureRequest
        ) -> tuple[CreateProjectRequest, str]:
            """不正な入力と期待するエラーメッセージを返す."""
            return request.param

        @pytest.fixture
        @classmethod
        def fixture_result(
            cls,
            fixture_repository: InMemoryProjectRepository,
            fixture_invalid_input: tuple[CreateProjectRequest, str],
        ) -> Result:
            """不正な入力で作成を実行した結果を返す."""
            return CreateProjectUseCase(fixture_repository).execute(
                fixture_invalid_input[0]
            )

        def test_実行が失敗する(self, fixture_result: Result) -> None:
            """検証エラーが失敗結果になることを確認する."""
            assert fixture_result.is_success is False

        def test_エラーコードがvalidation_errorになる(
            self, fixture_error: Error
        ) -> None:
            """エラーコードがVALIDATION_ERRORになることを確認する."""
            assert fixture_error.code is ErrorCode.VALIDATION_ERROR

        def test_検証エラーのメッセージが保持される(
            self,
            fixture_error: Error,
            fixture_invalid_input: tuple[CreateProjectRequest, str],
        ) -> None:
            """ドメインの検証エラーメッセージが保持されることを確認する."""
            assert fixture_error.message == fixture_invalid_input[1]

        @pytest.mark.usefixtures("fixture_result")
        def test_プロジェクトが保存されない(
            self, fixture_repository: InMemoryProjectRepository
        ) -> None:
            """検証エラー時には保存処理が行われないことを確認する."""
            assert fixture_repository.saved_projects == []

        def test_成功値が返されない(self, fixture_result: Result) -> None:
            """検証エラー時に成功値が設定されないことを確認する."""
            assert fixture_result.value is None

    class Testビジネスルール違反の場合は失敗する:
        """保存時のビジネスルール違反を失敗結果に変換する."""

        @pytest.fixture
        @classmethod
        def fixture_result(cls) -> Result:
            """保存がビジネスルール違反になる実行結果を返す."""
            use_case = CreateProjectUseCase(BusinessRuleViolationProjectRepository())
            return use_case.execute(CreateProjectRequest(name="テストプロジェクト"))

        def test_実行が失敗する(self, fixture_result: Result) -> None:
            """ビジネスルール違反が失敗結果になることを確認する."""
            assert fixture_result.is_success is False

        def test_エラーコードがbusiness_rule_violationになる(
            self, fixture_error: Error
        ) -> None:
            """エラーコードがBUSINESS_RULE_VIOLATIONになることを確認する."""
            assert fixture_error.code is ErrorCode.BUSINESS_RULE_VIOLATION

        def test_例外のメッセージが保持される(self, fixture_error: Error) -> None:
            """ビジネスルール違反のメッセージが保持されることを確認する."""
            assert fixture_error.message == "テストプロジェクトは作成できません"

        def test_成功値が返されない(self, fixture_result: Result) -> None:
            """保存失敗時に成功値が設定されないことを確認する."""
            assert fixture_result.value is None


class TestCompleteProjectUseCase:
    """CompleteProjectUseCaseのテスト."""

    @pytest.fixture
    @classmethod
    def fixture_response(cls, fixture_result: Result) -> CompleteProjectResponse:
        """実行結果からCompleteProjectResponseを取り出すフィクスチャ."""
        response = fixture_result.value
        assert isinstance(response, CompleteProjectResponse)
        return response

    class Test未完了タスクがあるプロジェクトを完了できる:
        """未完了タスクがあるプロジェクトを完了できる."""

        @pytest.fixture
        @classmethod
        def fixture_project_repository(cls) -> InMemoryProjectRepository:
            """テスト用のProjectリポジトリを生成するフィクスチャ."""
            return InMemoryProjectRepository()

        @pytest.fixture
        @classmethod
        def fixture_task_repository(cls) -> InMemoryTaskRepository:
            """テスト用のTaskリポジトリを生成するフィクスチャ."""
            return InMemoryTaskRepository()

        @pytest.fixture
        @classmethod
        def fixture_notification_port(cls) -> SpyNotificationPort:
            """テスト用のSpyNotificationPortを生成するフィクスチャ."""
            return SpyNotificationPort()

        @pytest.fixture
        @classmethod
        def fixture_incomplete_task(cls) -> Task:
            """未完了のテスト用Taskを生成するフィクスチャ."""
            return Task(title="Incomplete Task", description="Test Description")

        @pytest.fixture
        @classmethod
        def fixture_done_task(cls) -> Task:
            """完了済みのテスト用Taskを生成するフィクスチャ."""
            task = Task(title="Done Task", description="Test Description")
            task.complete()
            return task

        @pytest.fixture
        @classmethod
        def fixture_project(
            cls,
            fixture_project_repository: InMemoryProjectRepository,
            fixture_incomplete_task: Task,
            fixture_done_task: Task,
        ) -> Project:
            """リポジトリに保存済みのテスト用Projectを生成するフィクスチャ."""
            project = Project(name="Test Project")
            project.add_task(fixture_incomplete_task)
            project.add_task(fixture_done_task)
            fixture_project_repository.save(project)
            fixture_project_repository.saved_projects.clear()
            return project

        @pytest.fixture
        @classmethod
        def fixture_result(
            cls,
            fixture_project_repository: InMemoryProjectRepository,
            fixture_task_repository: InMemoryTaskRepository,
            fixture_notification_port: SpyNotificationPort,
            fixture_project: Project,
        ) -> Result:
            """ユースケースを実行した結果を返すフィクスチャ."""
            use_case = CompleteProjectUseCase(
                project_repository=fixture_project_repository,
                task_repository=fixture_task_repository,
                notification_service=fixture_notification_port,
            )
            request = CompleteProjectRequest(
                project_id=str(fixture_project.id), completion_notes="完了メモ"
            )
            return use_case.execute(request)

        @pytest.fixture
        @classmethod
        def fixture_completed_project(
            cls, fixture_result: Result, fixture_project: Project
        ) -> Project:
            """ユースケースの実行成功後のProjectを返すフィクスチャ."""
            assert fixture_result.is_success is True
            return fixture_project

        @pytest.fixture
        @classmethod
        def fixture_completed_at(
            cls, fixture_completed_project: Project
        ) -> dt.datetime:
            """完了済みProjectの完了時刻を返すフィクスチャ."""
            completed_at = fixture_completed_project.completed_at
            assert completed_at is not None
            return completed_at

        def test_実行が成功する(self, fixture_result: Result) -> None:
            """ユースケースの実行が成功することを確認する."""
            assert fixture_result.is_success is True

        def test_valueにprojectのidが設定される(
            self, fixture_response: CompleteProjectResponse, fixture_project: Project
        ) -> None:
            """valueにProjectのidが文字列で設定されることを確認する."""
            assert fixture_response.id == str(fixture_project.id)

        def test_valueのstatusがcompletedになる(
            self, fixture_response: CompleteProjectResponse
        ) -> None:
            """valueのstatusが文字列のCOMPLETEDになることを確認する."""
            assert fixture_response.status == ProjectStatus.COMPLETED.value

        def test_valueのcompletion_dateが完了時刻になる(
            self,
            fixture_response: CompleteProjectResponse,
            fixture_completed_at: dt.datetime,
        ) -> None:
            """valueのcompletion_dateがProjectの完了時刻のISO形式になることを確認する."""
            assert fixture_response.completion_date == fixture_completed_at

        def test_valueのtask_countがタスク数になる(
            self, fixture_response: CompleteProjectResponse
        ) -> None:
            """valueのtask_countがProjectのタスク数になることを確認する."""
            assert fixture_response.task_count == 2  # noqa: PLR2004

        def test_valueのcompletion_notesが設定される(
            self, fixture_response: CompleteProjectResponse
        ) -> None:
            """valueのcompletion_notesに指定したnotesが設定されることを確認する."""
            assert fixture_response.completion_notes == "完了メモ"

        def test_projectのstatusがcompletedになる(
            self, fixture_completed_project: Project
        ) -> None:
            """ProjectのstatusがCOMPLETEDになることを確認する."""
            assert fixture_completed_project.status is ProjectStatus.COMPLETED

        @pytest.mark.usefixtures("fixture_completed_project")
        def test_未完了タスクのstatusがdoneになる(
            self, fixture_incomplete_task: Task
        ) -> None:
            """未完了だったTaskのstatusがDONEになることを確認する."""
            assert fixture_incomplete_task.status is TaskStatus.DONE

        @pytest.mark.usefixtures("fixture_completed_project")
        def test_未完了だったタスクのみリポジトリに保存される(
            self,
            fixture_task_repository: InMemoryTaskRepository,
            fixture_incomplete_task: Task,
        ) -> None:
            """未完了だったTaskのみがリポジトリに保存されることを確認する."""
            assert fixture_task_repository.saved_tasks == [fixture_incomplete_task]

        @pytest.mark.usefixtures("fixture_completed_project")
        def test_未完了だったタスクの完了通知が送信される(
            self,
            fixture_notification_port: SpyNotificationPort,
            fixture_incomplete_task: Task,
        ) -> None:
            """未完了だったTaskの完了通知が送信されることを確認する."""
            assert [task.id for task in fixture_notification_port.completed_tasks] == [
                fixture_incomplete_task.id
            ]

        def test_projectがリポジトリに保存される(
            self,
            fixture_completed_project: Project,
            fixture_project_repository: InMemoryProjectRepository,
        ) -> None:
            """完了したProjectがリポジトリに保存されることを確認する."""
            assert fixture_project_repository.saved_projects == [
                fixture_completed_project
            ]

    class TestNotesを指定せずに完了できる:
        """notesを指定せずにプロジェクトを完了できる."""

        @pytest.fixture
        @classmethod
        def fixture_result(cls) -> Result:
            """notesを指定せずにユースケースを実行した結果を返すフィクスチャ."""
            project_repository = InMemoryProjectRepository()
            project = Project(name="Test Project")
            project_repository.save(project)
            use_case = CompleteProjectUseCase(
                project_repository=project_repository,
                task_repository=InMemoryTaskRepository(),
                notification_service=SpyNotificationPort(),
            )
            return use_case.execute(CompleteProjectRequest(project_id=str(project.id)))

        def test_実行が成功する(self, fixture_result: Result) -> None:
            """ユースケースの実行が成功することを確認する."""
            assert fixture_result.is_success is True

        def test_valueのcompletion_notesはnoneのまま(
            self, fixture_response: CompleteProjectResponse
        ) -> None:
            """valueのcompletion_notesがNoneのままであることを確認する."""
            assert fixture_response.completion_notes is None

    class Test存在しないprojectの場合は失敗する:
        """存在しないProjectを指定した場合は失敗結果が返る."""

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_project_id(cls) -> UUID:
            """存在しないProjectのidを生成するフィクスチャ."""
            return uuid4()

        @pytest.fixture
        @classmethod
        def fixture_result(cls, fixture_project_id: UUID) -> Result:
            """空のリポジトリでユースケースを実行した結果を返すフィクスチャ."""
            use_case = CompleteProjectUseCase(
                project_repository=InMemoryProjectRepository(),
                task_repository=InMemoryTaskRepository(),
                notification_service=SpyNotificationPort(),
            )
            return use_case.execute(
                CompleteProjectRequest(project_id=str(fixture_project_id))
            )

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

        def test_errorのmessageにproject_idが含まれる(
            self, fixture_error: Error, fixture_project_id: UUID
        ) -> None:
            """errorのmessageにProjectのidが含まれることを確認する."""
            assert str(fixture_project_id) in fixture_error.message

    class Test検証エラーの場合は失敗する:
        """Taskのcompleteが検証エラーを送出した場合は失敗結果が返る."""

        @pytest.fixture
        @classmethod
        def fixture_result(cls) -> Result:
            """検証エラーを送出するTaskを含むProjectで実行した結果を返すフィクスチャ."""
            project_repository = InMemoryProjectRepository()
            project = Project(name="Test Project")
            task = ValidationErrorTask(
                title="Test Task", description="Test Description"
            )
            project.add_task(task)
            project_repository.save(project)
            use_case = CompleteProjectUseCase(
                project_repository=project_repository,
                task_repository=InMemoryTaskRepository(),
                notification_service=SpyNotificationPort(),
            )
            return use_case.execute(CompleteProjectRequest(project_id=str(project.id)))

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

    class Testビジネスルール違反の場合は失敗する:
        """Taskのcompleteがビジネスルール違反を送出した場合は失敗結果が返る."""

        @pytest.fixture
        @classmethod
        def fixture_project_repository(cls) -> InMemoryProjectRepository:
            """空のProjectリポジトリを返す."""
            return InMemoryProjectRepository()

        @pytest.fixture
        @classmethod
        def fixture_task_repository(cls) -> InMemoryTaskRepository:
            """空のTaskリポジトリを返す."""
            return InMemoryTaskRepository()

        @pytest.fixture
        @classmethod
        def fixture_task(cls) -> Task:
            """状態変更後にビジネスルール違反を送出するTaskを返す."""
            return BusinessRuleViolationTask(
                title="Test Task", description="Test Description"
            )

        @pytest.fixture
        @classmethod
        def fixture_project(
            cls,
            fixture_project_repository: InMemoryProjectRepository,
            fixture_task: Task,
        ) -> Project:
            """対象Taskを含むProjectをリポジトリに保存する."""
            project = Project(name="Test Project")
            project.add_task(fixture_task)
            fixture_project_repository.save(project)
            fixture_project_repository.saved_projects.clear()
            return project

        @pytest.fixture
        @classmethod
        def fixture_result(
            cls,
            fixture_project_repository: InMemoryProjectRepository,
            fixture_task_repository: InMemoryTaskRepository,
            fixture_project: Project,
        ) -> Result:
            """ビジネスルール違反となる実行結果を返す."""
            use_case = CompleteProjectUseCase(
                project_repository=fixture_project_repository,
                task_repository=fixture_task_repository,
                notification_service=SpyNotificationPort(),
            )
            request = CompleteProjectRequest(project_id=str(fixture_project.id))
            return use_case.execute(request)

        @pytest.fixture
        @classmethod
        def fixture_error(cls, fixture_result: Result) -> Error:
            """実行結果からerrorを取り出す."""
            error = fixture_result.error
            assert error is not None
            return error

        def test_実行が失敗する(self, fixture_result: Result) -> None:
            """ビジネスルール違反が失敗結果になることを確認する."""
            assert fixture_result.is_success is False

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

        @pytest.mark.usefixtures("fixture_result")
        def test_task状態が実行前に復元される(
            self,
            fixture_project_repository: InMemoryProjectRepository,
            fixture_task_repository: InMemoryTaskRepository,
            fixture_project: Project,
            fixture_task: Task,
        ) -> None:
            """ProjectとTaskが実行前の状態に復元されることを確認する."""
            project = fixture_project_repository.get(fixture_project.id)
            task = fixture_task_repository.get(fixture_task.id)
            assert (project.status, task.status, task.completion_notes) == (
                ProjectStatus.ACTIVE,
                TaskStatus.TODO,
                None,
            )
