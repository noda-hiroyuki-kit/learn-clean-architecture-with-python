# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""期限チェックユースケースのテスト."""

import datetime as dt
from unittest.mock import MagicMock, call, create_autospec
from uuid import UUID

import pytest

from todo_app.application.common.result import Error, ErrorCode, Result
from todo_app.application.repositories.task_repository import TaskRepository
from todo_app.application.service_ports.notifications import NotificationPort
from todo_app.application.use_cases.deadline_use_cases import CheckDeadlinesUseCase
from todo_app.domain.entities.task import Task
from todo_app.domain.exceptions import (
    BusinessRuleViolationError,
    TaskNotFoundError,
    ValidationError,
)
from todo_app.domain.value_object import Deadline


@pytest.fixture
def fixture_clock(monkeypatch: pytest.MonkeyPatch) -> dt.datetime:
    """期限の生成後も時刻を固定できるよう、現在より先の日時を返す."""
    now = dt.datetime.now(tz=dt.UTC) + dt.timedelta(days=3)
    real_datetime = dt.datetime

    class StubDatetime(real_datetime):
        @classmethod
        def now(cls, tz: dt.tzinfo | None = None) -> dt.datetime:
            return now if tz is None else now.astimezone(tz)

    monkeypatch.setattr(dt, "datetime", StubDatetime)
    return now


@pytest.fixture
def fixture_repository() -> MagicMock:
    """TaskRepositoryのモックを返す."""
    return create_autospec(TaskRepository, instance=True)


@pytest.fixture
def fixture_notification_service() -> MagicMock:
    """NotificationPortのモックを返す."""
    return create_autospec(NotificationPort, instance=True)


class TestCheckDeadlinesUseCase:
    """CheckDeadlinesUseCaseのテスト."""

    class Test期限が近いタスクに通知する:
        """未完了タスクの期限に応じて通知する."""

        @pytest.fixture
        @classmethod
        def fixture_tasks(cls, fixture_clock: dt.datetime) -> list[Task]:
            """期限なし、期限到達、しきい値内外のタスクを返す."""
            return [
                Task(title="期限なし", description=""),
                Task(
                    title="期限到達", description="", due_date=Deadline(fixture_clock)
                ),
                Task(
                    title="期限まで半日",
                    description="",
                    due_date=Deadline(fixture_clock + dt.timedelta(hours=12)),
                ),
                Task(
                    title="しきい値ちょうど",
                    description="",
                    due_date=Deadline(fixture_clock + dt.timedelta(days=1)),
                ),
                Task(
                    title="しきい値超過",
                    description="",
                    due_date=Deadline(
                        fixture_clock + dt.timedelta(days=1, microseconds=1)
                    ),
                ),
            ]

        @pytest.fixture
        @classmethod
        def fixture_result(
            cls,
            fixture_repository: MagicMock,
            fixture_notification_service: MagicMock,
            fixture_tasks: list[Task],
        ) -> Result:
            """複数の期限をチェックした結果を返す."""
            fixture_repository.get_active_tasks.return_value = fixture_tasks
            return CheckDeadlinesUseCase(
                fixture_repository, fixture_notification_service
            ).execute()

        def test_通知件数を返す(self, fixture_result: Result) -> None:
            """しきい値以内のタスク数が返されることを確認する."""
            assert fixture_result.value == {"notifications_sent": 2}

        @pytest.mark.usefixtures("fixture_result")
        def test_対象タスクと残り日数を通知する(
            self, fixture_notification_service: MagicMock, fixture_tasks: list[Task]
        ) -> None:
            """対象タスクだけに残り日数を添えて通知する."""
            assert (
                fixture_notification_service.notify_task_deadline_approaching.call_args_list
                == [call(fixture_tasks[2], 0), call(fixture_tasks[3], 1)]
            )

    @pytest.mark.parametrize(
        "case",
        [(2, 1, 2), (4, 0, None)],
    )
    def test_指定したしきい値で判定する(
        self,
        fixture_clock: dt.datetime,
        fixture_repository: MagicMock,
        fixture_notification_service: MagicMock,
        case: tuple[int, int, int | None],
    ) -> None:
        """既定値とは異なるしきい値と残り日数で通知する."""
        days, expected_count, expected_days = case
        task = Task(
            title="期限あり",
            description="",
            due_date=Deadline(fixture_clock + dt.timedelta(days=days, hours=12)),
        )
        fixture_repository.get_active_tasks.return_value = [task]
        result = CheckDeadlinesUseCase(
            fixture_repository,
            fixture_notification_service,
            warning_threshold=dt.timedelta(days=3),
        ).execute()
        expected_calls = [] if expected_days is None else [call(task, expected_days)]
        assert (
            result.value,
            fixture_notification_service.notify_task_deadline_approaching.call_args_list,
        ) == ({"notifications_sent": expected_count}, expected_calls)

    def test_対象タスクがないと通知しない(
        self, fixture_repository: MagicMock, fixture_notification_service: MagicMock
    ) -> None:
        """アクティブなタスクがない場合は通知件数ゼロを返す."""
        fixture_repository.get_active_tasks.return_value = []
        result = CheckDeadlinesUseCase(
            fixture_repository, fixture_notification_service
        ).execute()
        assert (
            result.value,
            fixture_notification_service.notify_task_deadline_approaching.call_count,
        ) == ({"notifications_sent": 0}, 0)

    def test_期限切れタスクには通知しない(
        self,
        fixture_clock: dt.datetime,
        fixture_repository: MagicMock,
        fixture_notification_service: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """期限を過ぎたタスクは通知対象に含めない."""
        task = Task(title="期限切れ", description="", due_date=Deadline(fixture_clock))
        real_datetime = dt.datetime

        class StubDatetime(real_datetime):
            @classmethod
            def now(cls, tz: dt.tzinfo | None = None) -> dt.datetime:
                now = fixture_clock + dt.timedelta(seconds=1)
                return now if tz is None else now.astimezone(tz)

        monkeypatch.setattr(dt, "datetime", StubDatetime)
        fixture_repository.get_active_tasks.return_value = [task]
        result = CheckDeadlinesUseCase(
            fixture_repository, fixture_notification_service
        ).execute()
        assert (
            result.value,
            fixture_notification_service.notify_task_deadline_approaching.call_count,
        ) == ({"notifications_sent": 0}, 0)

    @pytest.mark.parametrize(
        ("error", "expected"),
        [
            (
                TaskNotFoundError(UUID("12345678-1234-5678-1234-567812345678")),
                Error.not_found(
                    "Task",
                    str(
                        TaskNotFoundError(UUID("12345678-1234-5678-1234-567812345678"))
                    ),
                ),
            ),
            (
                ValidationError("検証エラー"),
                Error(ErrorCode.VALIDATION_ERROR, "検証エラー"),
            ),
            (
                BusinessRuleViolationError("ルール違反"),
                Error(ErrorCode.BUSINESS_RULE_VIOLATION, "ルール違反"),
            ),
        ],
    )
    def test_リポジトリの例外を失敗結果に変換する(
        self,
        fixture_repository: MagicMock,
        fixture_notification_service: MagicMock,
        error: Exception,
        expected: Error,
    ) -> None:
        """リポジトリのドメイン例外を対応するエラー結果に変換する."""
        fixture_repository.get_active_tasks.side_effect = error
        result = CheckDeadlinesUseCase(
            fixture_repository, fixture_notification_service
        ).execute()
        assert result == Result.failure(expected)

    def test_通知時の検証エラーを失敗結果に変換する(
        self,
        fixture_clock: dt.datetime,
        fixture_repository: MagicMock,
        fixture_notification_service: MagicMock,
    ) -> None:
        """通知に失敗した場合は成功件数を返さず検証エラーを返す."""
        task = Task(
            title="期限あり",
            description="",
            due_date=Deadline(fixture_clock + dt.timedelta(hours=1)),
        )
        fixture_repository.get_active_tasks.return_value = [task]
        fixture_notification_service.notify_task_deadline_approaching.side_effect = (
            ValidationError("通知できません")
        )
        result = CheckDeadlinesUseCase(
            fixture_repository, fixture_notification_service
        ).execute()
        assert result == Result.failure(
            Error(ErrorCode.VALIDATION_ERROR, "通知できません")
        )
