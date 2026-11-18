# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""TaskControllerのテスト."""

from unittest.mock import Mock, call
from uuid import UUID

import pytest

from todo_app.application.common.result import Error, Result
from todo_app.application.dtos.task_dto import (
    CompleteTaskRequest,
    CreateTaskRequest,
    TaskResponse,
)
from todo_app.application.use_cases.task_use_cases import (
    CompleteTaskUseCase,
    CreateTaskUseCase,
    GetTaskUseCase,
)
from todo_app.domain.value_object import Priority, TaskStatus
from todo_app.interfaces.controllers.task_controller import TaskController
from todo_app.interfaces.presenters.base import TaskPresenter
from todo_app.interfaces.view_models.base import ErrorViewModel
from todo_app.interfaces.view_models.task_vm import TaskViewModel


class TestTaskController:
    """TaskControllerのテスト."""

    class TestHandleGet:
        """handle_getのテスト."""

        @pytest.fixture
        def fixture_controller(self) -> tuple[TaskController, Mock, Mock]:
            """テスト用のTaskControllerを生成する."""
            get_use_case = Mock(spec=GetTaskUseCase)
            presenter = Mock(spec=TaskPresenter)
            controller = TaskController(
                create_use_case=Mock(spec=CreateTaskUseCase),
                get_use_case=get_use_case,
                complete_use_case=Mock(spec=CompleteTaskUseCase),
                presenter=presenter,
            )
            return controller, get_use_case, presenter

        def test_取得成功時に表示モデルを返す(
            self, fixture_controller: tuple[TaskController, Mock, Mock]
        ) -> None:
            """取得結果を表示モデルに変換して返すことを確認する."""
            controller, get_use_case, presenter = fixture_controller
            task_id = "12345678-1234-5678-1234-567812345678"
            response = TaskResponse(
                id=task_id,
                title="タスク",
                description="説明",
                status=TaskStatus.TODO,
                priority=Priority.MEDIUM,
            )
            view_model = TaskViewModel(
                id=task_id,
                title="タスク",
                description="説明",
                status_display="未着手",
                priority_display="中",
                due_date_display=None,
                project_display=None,
                completion_info=None,
            )
            get_use_case.execute.return_value = Result.success(response)
            presenter.present_task.return_value = view_model

            result = controller.handle_get(task_id)

            assert (
                result.success,
                get_use_case.execute.call_args,
                presenter.present_task.call_args,
            ) == (
                view_model,
                call(UUID(task_id)),
                call(response),
            )

        def test_ユースケースの失敗を表示モデルに変換する(
            self, fixture_controller: tuple[TaskController, Mock, Mock]
        ) -> None:
            """ユースケースのエラーを表示モデルに変換して返すことを確認する."""
            controller, get_use_case, presenter = fixture_controller
            task_id = "12345678-1234-5678-1234-567812345678"
            error = Error.not_found("Task", task_id)
            error_view_model = ErrorViewModel(
                message=f"id {task_id} の Task が見つかりません",
                code="NOT_FOUND",
            )
            get_use_case.execute.return_value = Result.failure(error)
            presenter.present_error.return_value = error_view_model

            result = controller.handle_get(task_id)

            assert (
                result.error,
                presenter.present_error.call_args,
            ) == (
                error_view_model,
                call(f"id {task_id} の Task が見つかりません", "NOT_FOUND"),
            )

        def test_uuid形式でないtask_idを検証エラーに変換する(
            self, fixture_controller: tuple[TaskController, Mock, Mock]
        ) -> None:
            """UUID形式でないtask_idを検証エラーとして返すことを確認する."""
            controller, get_use_case, presenter = fixture_controller
            error_view_model = ErrorViewModel(
                message="badly formed hexadecimal UUID string",
                code="VALIDATION_ERROR",
            )
            presenter.present_error.return_value = error_view_model

            result = controller.handle_get("invalid-task-id")

            assert (
                result.error,
                get_use_case.execute.call_args,
                presenter.present_error.call_args,
            ) == (
                error_view_model,
                None,
                call("badly formed hexadecimal UUID string", "VALIDATION_ERROR"),
            )

    class TestHandleCreate:
        """handle_createのテスト."""

        @pytest.fixture
        def fixture_controller(self) -> tuple[TaskController, Mock, Mock]:
            """テスト用のTaskControllerを生成する."""
            create_use_case = Mock(spec=CreateTaskUseCase)
            complete_use_case = Mock(spec=CompleteTaskUseCase)
            presenter = Mock(spec=TaskPresenter)
            controller = TaskController(
                create_use_case=create_use_case,
                get_use_case=Mock(spec=GetTaskUseCase),
                complete_use_case=complete_use_case,
                presenter=presenter,
            )
            return controller, create_use_case, presenter

        def test_作成成功時に表示モデルを返す(
            self, fixture_controller: tuple[TaskController, Mock, Mock]
        ) -> None:
            """作成結果を表示モデルに変換して返すことを確認する."""
            controller, create_use_case, presenter = fixture_controller
            response = TaskResponse(
                id="task-id",
                title="タスク",
                description="説明",
                status=TaskStatus.TODO,
                priority=Priority.MEDIUM,
            )
            view_model = TaskViewModel(
                id="task-id",
                title="タスク",
                description="説明",
                status_display="未着手",
                priority_display="中",
                due_date_display=None,
                project_display=None,
                completion_info=None,
            )
            create_use_case.execute.return_value = Result.success(response)
            presenter.present_task.return_value = view_model

            result = controller.handle_create("タスク", "説明")

            assert (
                result.success,
                create_use_case.execute.call_args,
                presenter.present_task.call_args,
            ) == (
                view_model,
                call(CreateTaskRequest(title="タスク", description="説明")),
                call(response),
            )

        def test_ユースケースの失敗を表示モデルに変換する(
            self, fixture_controller: tuple[TaskController, Mock, Mock]
        ) -> None:
            """ユースケースのエラーを表示モデルに変換して返すことを確認する."""
            controller, create_use_case, presenter = fixture_controller
            error = Error.validation_error("入力が不正です")
            error_view_model = ErrorViewModel(
                message="入力が不正です", code="VALIDATION_ERROR"
            )
            create_use_case.execute.return_value = Result.failure(error)
            presenter.present_error.return_value = error_view_model

            result = controller.handle_create("タスク", "説明")

            assert (
                result.error,
                presenter.present_error.call_args,
            ) == (
                error_view_model,
                call("入力が不正です", "VALIDATION_ERROR"),
            )

        def test_value_errorを検証エラーに変換する(
            self, fixture_controller: tuple[TaskController, Mock, Mock]
        ) -> None:
            """ValueErrorを検証エラーとして返すことを確認する."""
            controller, create_use_case, presenter = fixture_controller
            create_use_case.execute.side_effect = ValueError("入力値が不正です")
            error_view_model = ErrorViewModel(
                message="入力値が不正です", code="VALIDATION_ERROR"
            )
            presenter.present_error.return_value = error_view_model

            result = controller.handle_create("タスク", "説明")

            assert (
                result.error,
                presenter.present_error.call_args,
            ) == (
                error_view_model,
                call("入力値が不正です", "VALIDATION_ERROR"),
            )

    class TestHandleComplete:
        """handle_completeのテスト."""

        @pytest.fixture
        def fixture_controller(self) -> tuple[TaskController, Mock, Mock]:
            """テスト用のTaskControllerを生成する."""
            create_use_case = Mock(spec=CreateTaskUseCase)
            complete_use_case = Mock(spec=CompleteTaskUseCase)
            presenter = Mock(spec=TaskPresenter)
            controller = TaskController(
                create_use_case=create_use_case,
                get_use_case=Mock(spec=GetTaskUseCase),
                complete_use_case=complete_use_case,
                presenter=presenter,
            )
            return controller, complete_use_case, presenter

        def test_完了成功時に表示モデルを返す(
            self, fixture_controller: tuple[TaskController, Mock, Mock]
        ) -> None:
            """完了結果を表示モデルに変換して返すことを確認する."""
            controller, complete_use_case, presenter = fixture_controller
            response = TaskResponse(
                id="task-id",
                title="タスク",
                description="説明",
                status=TaskStatus.DONE,
                priority=Priority.MEDIUM,
            )
            view_model = TaskViewModel(
                id="task-id",
                title="タスク",
                description="説明",
                status_display="完了",
                priority_display="中",
                due_date_display=None,
                project_display=None,
                completion_info=None,
            )
            complete_use_case.execute.return_value = Result.success(response)
            presenter.present_task.return_value = view_model

            result = controller.handle_complete(
                "12345678-1234-5678-1234-567812345678", "完了メモ"
            )

            assert (
                result.success,
                complete_use_case.execute.call_args,
                presenter.present_task.call_args,
            ) == (
                view_model,
                call(
                    CompleteTaskRequest(
                        task_id="12345678-1234-5678-1234-567812345678",
                        completion_notes="完了メモ",
                    )
                ),
                call(response),
            )

        def test_ユースケースの失敗を表示モデルに変換する(
            self, fixture_controller: tuple[TaskController, Mock, Mock]
        ) -> None:
            """ユースケースのエラーを表示モデルに変換して返すことを確認する."""
            controller, complete_use_case, presenter = fixture_controller
            error = Error.validation_error("入力が不正です")
            error_view_model = ErrorViewModel(
                message="入力が不正です", code="VALIDATION_ERROR"
            )
            complete_use_case.execute.return_value = Result.failure(error)
            presenter.present_error.return_value = error_view_model

            result = controller.handle_complete("12345678-1234-5678-1234-567812345678")

            assert (
                result.error,
                presenter.present_error.call_args,
            ) == (
                error_view_model,
                call("入力が不正です", "VALIDATION_ERROR"),
            )

        def test_value_errorを検証エラーに変換する(
            self, fixture_controller: tuple[TaskController, Mock, Mock]
        ) -> None:
            """ValueErrorを検証エラーとして返すことを確認する."""
            controller, complete_use_case, presenter = fixture_controller
            complete_use_case.execute.side_effect = ValueError("入力値が不正です")
            error_view_model = ErrorViewModel(
                message="入力値が不正です", code="VALIDATION_ERROR"
            )
            presenter.present_error.return_value = error_view_model

            result = controller.handle_complete("invalid-task-id")

            assert (
                result.error,
                presenter.present_error.call_args,
            ) == (
                error_view_model,
                call("タスク ID の形式が無効です", "VALIDATION_ERROR"),
            )
