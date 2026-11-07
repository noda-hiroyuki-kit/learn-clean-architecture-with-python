# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""Projectエンティティのテスト."""

from typing import TYPE_CHECKING
from uuid import UUID

import pytest

from todo_app.domain.entities.project import Project
from todo_app.domain.entities.task import Task
from todo_app.domain.value_object import ProjectStatus

if TYPE_CHECKING:
    import datetime as dt


class TestProject:
    """Projectエンティティのテスト."""

    class TestProjectが正しく生成される:
        """Projectが正しく生成される."""

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_project(cls) -> Project:
            """テスト用のProjectを生成するフィクスチャ."""
            return Project(
                name="Test Project",
                description="Test Description",
            )

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_project_without_description(cls) -> Project:
            """descriptionなしのテスト用Projectを生成するフィクスチャ."""
            return Project(name="Test Project Without Description")

        def test_名前が設定される(self, fixture_project: Project) -> None:
            """名前が設定されることを確認する."""
            assert fixture_project.name == "Test Project"

        def test_idが自動生成される(self, fixture_project: Project) -> None:
            """idが自動生成されることを確認する."""
            assert fixture_project.id is not None

        def test_descriptionが設定される(self, fixture_project: Project) -> None:
            """descriptionが設定されることを確認する."""
            assert fixture_project.description == "Test Description"

        def test_規定値のdescriptionが文字列長0で設定される(
            self, fixture_project_without_description: Project
        ) -> None:
            """descriptionが規定値で文字列長0で設定されることを確認する."""
            assert fixture_project_without_description.description == ""

        def test_statusの初期値はACTIVEである(self, fixture_project: Project) -> None:
            """statusの初期値がACTIVEであることを確認する."""
            assert fixture_project.status is ProjectStatus.ACTIVE

        def test_completed_atの初期値はNoneである(
            self, fixture_project: Project
        ) -> None:
            """completed_atの初期値がNoneであることを確認する."""
            assert fixture_project.completed_at is None

        def test_completion_notesの初期値はNoneである(
            self, fixture_project: Project
        ) -> None:
            """completion_notesの初期値がNoneであることを確認する."""
            assert fixture_project.completion_notes is None

    class TestProjectのメソッドのテスト:
        """Projectのメソッドに関するテスト."""

        @pytest.fixture
        @classmethod
        def fixture_project(cls) -> Project:
            """テスト用のProjectを生成するフィクスチャ."""
            return Project(
                name="Test Project",
                description="Test Description",
            )

        @pytest.fixture
        @classmethod
        def fixture_task(cls) -> Task:
            """テスト用のTaskを生成するフィクスチャ."""
            return Task(
                title="Test Task",
                description="Test Description",
            )

        def test_add_taskでタスクが追加される(
            self, fixture_project: Project, fixture_task: Task
        ) -> None:
            """add_taskでタスクが追加されることを確認する."""
            fixture_project.add_task(fixture_task)
            assert fixture_project.get_task(fixture_task.id) is fixture_task

        def test_add_taskでタスクのproject_idが設定される(
            self, fixture_project: Project, fixture_task: Task
        ) -> None:
            """add_taskでタスクのproject_idが設定されることを確認する."""
            fixture_project.add_task(fixture_task)
            assert fixture_task.project_id == fixture_project.id

        def test_完了したプロジェクトにタスクを追加するとValueErrorになる(
            self, fixture_project: Project, fixture_task: Task
        ) -> None:
            """完了したプロジェクトにタスクを追加するとValueErrorになることを確認する."""
            fixture_project.mark_completed()
            with pytest.raises(
                ValueError, match="完了したプロジェクトにはタスクを追加できません"
            ):
                fixture_project.add_task(fixture_task)

        def test_get_taskで追加したタスクが取得できる(
            self, fixture_project: Project, fixture_task: Task
        ) -> None:
            """get_taskで追加したタスクが取得できることを確認する."""
            fixture_project.add_task(fixture_task)
            task = fixture_project.get_task(fixture_task.id)
            assert task is fixture_task

        def test_get_taskで存在しないタスクはNoneが返る(
            self, fixture_project: Project
        ) -> None:
            """get_taskで存在しないタスクはNoneが返ることを確認する."""
            task = fixture_project.get_task(
                UUID("12345678-1234-5678-1234-567812345678")
            )
            assert task is None

        def test_remove_taskでタスクが削除される(
            self, fixture_project: Project, fixture_task: Task
        ) -> None:
            """remove_taskでタスクが削除されることを確認する."""
            fixture_project.add_task(fixture_task)
            fixture_project.remove_task(fixture_task.id)
            assert fixture_project.get_task(fixture_task.id) is None

        def test_remove_taskでタスクのproject_idがNoneになる(
            self, fixture_project: Project, fixture_task: Task
        ) -> None:
            """remove_taskでタスクのproject_idがNoneになることを確認する."""
            fixture_project.add_task(fixture_task)
            fixture_project.remove_task(fixture_task.id)
            assert fixture_task.project_id is None

        def test_remove_taskで存在しないタスクを削除してもエラーにならない(
            self, fixture_project: Project
        ) -> None:
            """remove_taskで存在しないタスクを削除してもエラーにならないことを確認する."""
            fixture_project.remove_task(UUID("12345678-1234-5678-1234-567812345678"))
            assert fixture_project.tasks == []

        def test_tasksでタスクの一覧が取得できる(
            self, fixture_project: Project, fixture_task: Task
        ) -> None:
            """tasksでタスクの一覧が取得できることを確認する."""
            fixture_project.add_task(fixture_task)
            assert fixture_project.tasks == [fixture_task]

        def test_タスクが追加されていないときはtasksは空のリストを返す(
            self, fixture_project: Project
        ) -> None:
            """タスクが追加されていないときはtasksが空のリストを返すことを確認する."""
            assert fixture_project.tasks == []

        def test_incomplete_tasksで未完了のタスクのみ取得できる(
            self, fixture_project: Project, fixture_task: Task
        ) -> None:
            """incomplete_tasksで未完了のタスクのみ取得できることを確認する."""
            done_task = Task(title="Done Task", description="Done Description")
            fixture_project.add_task(fixture_task)
            fixture_project.add_task(done_task)
            done_task.complete()
            assert fixture_project.incomplete_tasks == [fixture_task]

        def test_全てのタスクが完了しているときはincomplete_tasksは空のリストを返す(
            self, fixture_project: Project, fixture_task: Task
        ) -> None:
            """全てのタスクが完了しているときはincomplete_tasksが空のリストを返すことを確認する."""
            fixture_project.add_task(fixture_task)
            fixture_task.complete()
            assert fixture_project.incomplete_tasks == []

    class TestMarkCompletedでプロジェクトが完了する:
        """mark_completedでプロジェクトが完了することのテスト."""

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_completed_project(cls) -> Project:
            """mark_completed済みのテスト用Projectを生成するフィクスチャ."""
            project = Project(name="Test Project")
            project.mark_completed(notes="完了メモ")
            return project

        def test_statusがCOMPLETEDになる(
            self, fixture_completed_project: Project
        ) -> None:
            """statusがCOMPLETEDになることを確認する."""
            assert fixture_completed_project.status is ProjectStatus.COMPLETED

        def test_completed_atが設定される(
            self, fixture_completed_project: Project
        ) -> None:
            """completed_atが設定されることを確認する."""
            assert fixture_completed_project.completed_at is not None

        def test_completion_notesが設定される(
            self, fixture_completed_project: Project
        ) -> None:
            """completion_notesが設定されることを確認する."""
            assert fixture_completed_project.completion_notes == "完了メモ"

        def test_notesを省略するとcompletion_notesはNoneになる(self) -> None:
            """notesを省略するとcompletion_notesがNoneになることを確認する."""
            project = Project(name="Test Project")
            project.mark_completed()
            assert project.completion_notes is None

    class Test完了済みプロジェクトでmarkCompletedを再度呼んでも状態が変わらない:
        """完了済みプロジェクトでmark_completedを再度呼んでも状態が変わらないことのテスト."""

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_twice_completed_project(cls) -> tuple[Project, dt.datetime | None]:
            """mark_completedを2回呼んだProjectと1回目のcompleted_atを返すフィクスチャ."""
            project = Project(name="Test Project")
            project.mark_completed(notes="最初のメモ")
            first_completed_at = project.completed_at
            project.mark_completed(notes="2回目のメモ")
            return project, first_completed_at

        def test_completed_atが変わらない(
            self, fixture_twice_completed_project: tuple[Project, dt.datetime | None]
        ) -> None:
            """completed_atが変わらないことを確認する."""
            project, first_completed_at = fixture_twice_completed_project
            assert project.completed_at == first_completed_at

        def test_completion_notesが変わらない(
            self, fixture_twice_completed_project: tuple[Project, dt.datetime | None]
        ) -> None:
            """completion_notesが変わらないことを確認する."""
            project, _ = fixture_twice_completed_project
            assert project.completion_notes == "最初のメモ"
