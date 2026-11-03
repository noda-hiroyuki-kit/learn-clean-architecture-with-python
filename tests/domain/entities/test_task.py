# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""Taskエンティティのテスト."""

import datetime as dt
from uuid import UUID

import pytest

from todo_app.domain.entities.task import Task
from todo_app.domain.entities.value_object import Deadline, Priority, TaskStatus


class TestTask:
    """Taskエンティティのテスト."""

    class TestTaskが正しく生成される:
        """Taskが正しく生成される."""

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_task(cls) -> Task:
            """テスト用のTaskを生成するフィクスチャ."""
            return Task(
                title="Test Task",
                description="Test Description",
                project_id=UUID("12345678-1234-5678-1234-567812345678"),
            )

        def test_タイトルが設定される(self, fixture_task: Task) -> None:
            """タイトルが設定されることを確認する."""
            assert fixture_task.title == "Test Task"

        def test_idが自動生成される(self, fixture_task: Task) -> None:
            """idが自動生成されることを確認する."""
            assert fixture_task.id is not None

        def test_descriptionが設定される(self, fixture_task: Task) -> None:
            """descriptionが設定されることを確認する."""
            assert fixture_task.description == "Test Description"

        def test_project_idが設定される(self, fixture_task: Task) -> None:
            """project_idが設定されることを確認する."""
            assert fixture_task.project_id == UUID(
                "12345678-1234-5678-1234-567812345678"
            )

        def test_priorityは既定でMEDIUMに設定される(self, fixture_task: Task) -> None:
            """priorityが既定でMEDIUMに設定されることを確認する."""
            assert fixture_task.priority == Priority.MEDIUM

        def test_statusは既定でTODOに設定される(self, fixture_task: Task) -> None:
            """statusが既定でTODOに設定されることを確認する."""
            assert fixture_task.status == TaskStatus.TODO

    class TestTaskのStatus遷移テスト:
        """TaskのStatus遷移に関するテスト."""

        @pytest.fixture
        @classmethod
        def fixture_task(cls) -> Task:
            """テスト用のTaskを生成するフィクスチャ."""
            return Task(
                title="Complete project proposal",
                description="Draft and review the proposal for the new client project",
                project_id=UUID("12345678-1234-5678-1234-567812345678"),
                due_date=Deadline(dt.datetime.now(tz=dt.UTC) + dt.timedelta(days=7)),
                priority=Priority.HIGH,
            )

        def test_statusがtodoの時はstartできる(self, fixture_task: Task) -> None:
            """statusがTODOの時はstartできることを確認する."""
            fixture_task.start()
            assert fixture_task.status == TaskStatus.IN_PROGRESS

        def test_statusがin_progressの時はstartできない(
            self, fixture_task: Task
        ) -> None:
            """statusがIN_PROGRESSの時はstartできないことを確認する."""
            fixture_task.start()
            with pytest.raises(
                ValueError, match="TaskのstatusがTODOの場合のみ開始できます。"
            ):
                fixture_task.start()

        def test_statusがtodoの時はcompletedにできる(self, fixture_task: Task) -> None:
            """statusがTODOの時はcompletedにできることを確認する."""
            fixture_task.complete()
            assert fixture_task.status == TaskStatus.DONE

        def test_statusがin_progressの時はcompletedにできる(
            self, fixture_task: Task
        ) -> None:
            """statusがIN_PROGRESSの時はcompletedにできることを確認する."""
            fixture_task.start()
            fixture_task.complete()
            assert fixture_task.status == TaskStatus.DONE

        def test_statusがdoneの時はcompletedにできない(
            self, fixture_task: Task
        ) -> None:
            """statusがDONEの時はcompletedにできないことを確認する."""
            fixture_task.complete()
            with pytest.raises(ValueError, match="Taskは既に完了しています。"):
                fixture_task.complete()
