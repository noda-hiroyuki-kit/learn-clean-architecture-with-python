# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""NotificationPortのテスト."""

import pytest

from todo_app.application.service_ports.notifications import NotificationPort
from todo_app.domain.entities.task import Task


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


class DelegatingNotificationPort(NotificationPort):
    """基底クラスの抽象メソッドをそのまま呼び出すテスト用のNotificationPort実装."""

    def notify_task_completed(self, task: Task) -> None:
        """基底クラスのタスク完了の通知を呼び出す."""
        super().notify_task_completed(task)

    def notify_task_high_priority(self, task: Task) -> None:
        """基底クラスの高優先度タスクの通知を呼び出す."""
        super().notify_task_high_priority(task)

    def notify_task_deadline_approaching(self, task: Task, days_remaining: int) -> None:
        """基底クラスの締め切りが近づいたタスクの通知を呼び出す."""
        super().notify_task_deadline_approaching(task, days_remaining)


class TestNotificationPort:
    """NotificationPortのテスト."""

    class Test抽象クラスとしての振る舞い:
        """抽象クラスとしての振る舞いに関するテスト."""

        def test_直接インスタンス化できない(self) -> None:
            """NotificationPortを直接インスタンス化できないことを確認する."""
            with pytest.raises(TypeError):
                NotificationPort()  # type: ignore[abstract]

        def test_全ての抽象メソッドを実装したサブクラスはインスタンス化できる(
            self,
        ) -> None:
            """全ての抽象メソッドを実装したサブクラスはインスタンス化できることを確認する."""
            assert isinstance(SpyNotificationPort(), NotificationPort)

        def test_抽象メソッドが未実装のサブクラスはインスタンス化できない(self) -> None:
            """抽象メソッドが未実装のサブクラスはインスタンス化できないことを確認する."""

            class IncompleteNotificationPort(NotificationPort):
                """notify_task_completedのみ実装した不完全な実装."""

                def notify_task_completed(self, task: Task) -> None:
                    """タスク完了の通知を送信する."""

            with pytest.raises(TypeError):
                IncompleteNotificationPort()  # type: ignore[abstract]

    class Test基底クラスの抽象メソッドはNotImplementedErrorを送出する:
        """基底クラスの抽象メソッドがNotImplementedErrorを送出することのテスト."""

        @pytest.fixture
        @classmethod
        def fixture_port(cls) -> DelegatingNotificationPort:
            """基底クラスに委譲するテスト用のNotificationPortを生成するフィクスチャ."""
            return DelegatingNotificationPort()

        @pytest.fixture
        @classmethod
        def fixture_task(cls) -> Task:
            """テスト用のTaskを生成するフィクスチャ."""
            return Task(title="Test Task", description="Test Description")

        def test_notify_task_completedはNotImplementedErrorを送出する(
            self, fixture_port: DelegatingNotificationPort, fixture_task: Task
        ) -> None:
            """notify_task_completedがNotImplementedErrorを送出することを確認する."""
            with pytest.raises(NotImplementedError):
                fixture_port.notify_task_completed(fixture_task)

        def test_notify_task_high_priorityはNotImplementedErrorを送出する(
            self, fixture_port: DelegatingNotificationPort, fixture_task: Task
        ) -> None:
            """notify_task_high_priorityがNotImplementedErrorを送出することを確認する."""
            with pytest.raises(NotImplementedError):
                fixture_port.notify_task_high_priority(fixture_task)

        def test_notify_task_deadline_approachingはNotImplementedErrorを送出する(
            self, fixture_port: DelegatingNotificationPort, fixture_task: Task
        ) -> None:
            """notify_task_deadline_approachingがNotImplementedErrorを送出することを確認する."""
            with pytest.raises(NotImplementedError):
                fixture_port.notify_task_deadline_approaching(fixture_task, 3)

    class Test具象実装を通じて通知を送信できる:
        """具象実装を通じて通知を送信できることのテスト."""

        @pytest.fixture
        @classmethod
        def fixture_port(cls) -> SpyNotificationPort:
            """テスト用のSpyNotificationPortを生成するフィクスチャ."""
            return SpyNotificationPort()

        @pytest.fixture
        @classmethod
        def fixture_task(cls) -> Task:
            """テスト用のTaskを生成するフィクスチャ."""
            return Task(title="Test Task", description="Test Description")

        def test_notify_task_completedでタスク完了の通知が送信される(
            self, fixture_port: SpyNotificationPort, fixture_task: Task
        ) -> None:
            """notify_task_completedでタスク完了の通知が送信されることを確認する."""
            fixture_port.notify_task_completed(fixture_task)
            assert fixture_port.completed_tasks == [fixture_task]

        def test_notify_task_high_priorityで高優先度タスクの通知が送信される(
            self, fixture_port: SpyNotificationPort, fixture_task: Task
        ) -> None:
            """notify_task_high_priorityで高優先度タスクの通知が送信されることを確認する."""
            fixture_port.notify_task_high_priority(fixture_task)
            assert fixture_port.high_priority_tasks == [fixture_task]

        def test_notify_task_deadline_approachingで締め切りが近づいた通知が送信される(
            self, fixture_port: SpyNotificationPort, fixture_task: Task
        ) -> None:
            """notify_task_deadline_approachingで締め切りが近づいた通知が送信されることを確認する."""
            fixture_port.notify_task_deadline_approaching(fixture_task, 3)
            assert fixture_port.deadline_notifications == [(fixture_task, 3)]
