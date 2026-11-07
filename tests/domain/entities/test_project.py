# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""Projectエンティティのテスト."""

from uuid import UUID

import pytest

from todo_app.domain.entities.project import Project
from todo_app.domain.entities.task import Task
from todo_app.domain.value_object import ProjectStatus


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
