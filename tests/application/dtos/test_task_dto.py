# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""Taskデータ転送オブジェクトのテスト."""

from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from todo_app.application.dtos.task_dto import SetTaskPriorityRequest
from todo_app.domain.value_object import Priority

TASK_ID = "12345678-1234-5678-1234-567812345678"


class TestSetTaskPriorityRequest:
    """SetTaskPriorityRequestのテスト."""

    class Test正しく生成される:
        """SetTaskPriorityRequestが正しく生成される."""

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_request(cls) -> SetTaskPriorityRequest:
            """テスト用のSetTaskPriorityRequestを生成する."""
            return SetTaskPriorityRequest(task_id=TASK_ID, priority="HIGH")

        def test_task_idが設定される(
            self, fixture_request: SetTaskPriorityRequest
        ) -> None:
            """task_idが設定されることを確認する."""
            assert fixture_request.task_id == TASK_ID

        def test_priorityが設定される(
            self, fixture_request: SetTaskPriorityRequest
        ) -> None:
            """priorityが設定されることを確認する."""
            assert fixture_request.priority == "HIGH"

        def test_フィールドを変更できない(
            self, fixture_request: SetTaskPriorityRequest
        ) -> None:
            """リクエストのフィールドが変更できないことを確認する."""
            with pytest.raises(FrozenInstanceError, match="priority"):
                fixture_request.priority = "LOW"

    class Test検証エラーになる:
        """不正なリクエストデータの場合はValueErrorが送出される."""

        @pytest.mark.parametrize("task_id", ["", "   "])
        def test_task_idが空の場合はvalue_errorになる(self, task_id: str) -> None:
            """task_idが空または空白のみの場合はValueErrorになることを確認する."""
            with pytest.raises(ValueError, match="タスク ID が必要です"):
                SetTaskPriorityRequest(task_id=task_id, priority="HIGH")

        def test_task_idがuuid形式でない場合はvalue_errorになる(self) -> None:
            """task_idがUUID形式でない場合はValueErrorになることを確認する."""
            with pytest.raises(ValueError, match="タスク ID の形式が無効です"):
                SetTaskPriorityRequest(task_id="not-a-uuid", priority="HIGH")

        @pytest.mark.parametrize("priority", ["", "UNKNOWN"])
        def test_priorityが無効な場合はvalue_errorになる(self, priority: str) -> None:
            """priorityが有効な優先度でない場合はValueErrorになることを確認する."""
            with pytest.raises(ValueError, match="優先度は次のいずれか"):
                SetTaskPriorityRequest(task_id=TASK_ID, priority=priority)

    class TestToExecutionParamsでユースケース用のパラメータに変換できる:
        """to_execution_paramsでユースケース用のパラメータに変換できる."""

        @pytest.mark.parametrize(
            ("priority", "expected_priority"),
            [
                ("LOW", Priority.LOW),
                ("medium", Priority.MEDIUM),
                (" high　", Priority.HIGH),
            ],
        )
        def test_task_idがuuidに変換され優先度が正規化される(
            self, priority: str, expected_priority: Priority
        ) -> None:
            """task_idをUUIDに変換し、優先度の大小文字と空白を正規化する."""
            request = SetTaskPriorityRequest(task_id=TASK_ID, priority=priority)
            params = request.to_execution_params()
            assert params == {
                "task_id": UUID(TASK_ID),
                "priority": expected_priority,
            }
