# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""Projectエンティティのテスト."""

import pytest

from todo_app.domain.entities.project import Project


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
            )

        def test_名前が設定される(self, fixture_project: Project) -> None:
            """名前が設定されることを確認する."""
            assert fixture_project.name == "Test Project"

        def test_idが自動生成される(self, fixture_project: Project) -> None:
            """idが自動生成されることを確認する."""
            assert fixture_project.id is not None
