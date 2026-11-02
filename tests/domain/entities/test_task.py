# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""Taskエンティティのテスト."""

import pytest

from todo_app.domain.entities.task import Task


class TestTask:
    """Taskエンティティのテスト."""

    class TestTaskが正しく生成される:
        """Taskが正しく生成される."""

        @pytest.fixture(scope="class")
        def fixture_task(self) -> Task:
            """テスト用のTaskを生成するフィクスチャ."""
            return Task(title="Test Task", description="Test Description")

        def test_タイトルが設定される(self, fixture_task: Task) -> None:
            """タイトルが設定されることを確認する."""
            assert fixture_task.title == "Test Task"

        def test_idが自動生成される(self, fixture_task: Task) -> None:
            """idが自動生成されることを確認する."""
            assert fixture_task.id is not None

        def test_descriptionが設定される(self, fixture_task: Task) -> None:
            """descriptionが設定されることを確認する."""
            assert fixture_task.description == "Test Description"
