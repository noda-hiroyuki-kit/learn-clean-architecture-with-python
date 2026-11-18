# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""ProjectControllerのテスト."""

from unittest.mock import Mock, call

import pytest

from todo_app.application.common.result import Error, Result
from todo_app.application.dtos.project_dto import CreateProjectRequest, ProjectResponse
from todo_app.application.use_cases.project_use_cases import (
    CompleteProjectUseCase,
    CreateProjectUseCase,
    GetProjectUseCase,
    ListProjectsUseCase,
    UpdateProjectUseCase,
)
from todo_app.interfaces.controllers.project_controller import ProjectController
from todo_app.interfaces.presenters.base import ProjectPresenter
from todo_app.interfaces.view_models.base import ErrorViewModel
from todo_app.interfaces.view_models.project_vm import ProjectViewModel


class TestProjectController:
    """ProjectControllerのテスト."""

    class TestHandleCreate:
        """handle_createのテスト."""

        @pytest.fixture
        def fixture_controller(self) -> tuple[ProjectController, Mock, Mock]:
            """テスト用のProjectControllerを生成する."""
            create_use_case = Mock(spec=CreateProjectUseCase)
            presenter = Mock(spec=ProjectPresenter)
            controller = ProjectController(
                create_use_case=create_use_case,
                complete_use_case=Mock(spec=CompleteProjectUseCase),
                presenter=presenter,
                get_use_case=Mock(spec=GetProjectUseCase),
                list_use_case=Mock(spec=ListProjectsUseCase),
                update_use_case=Mock(spec=UpdateProjectUseCase),
            )
            return controller, create_use_case, presenter

        def test_作成成功時に表示モデルを返す(
            self, fixture_controller: tuple[ProjectController, Mock, Mock]
        ) -> None:
            """作成結果を表示モデルに変換して返すことを確認する."""
            controller, create_use_case, presenter = fixture_controller
            response = ProjectResponse(
                id="project-id",
                name="プロジェクト",
                description="説明",
                status="ACTIVE",
                completion_date=None,
                tasks=[],
            )
            view_model = ProjectViewModel(
                id="project-id",
                name="プロジェクト",
                description="説明",
                project_type="通常",
                status_display="進行中",
                task_count=0,
                completed_task_count=0,
                completion_info=None,
                tasks=[],
            )
            create_use_case.execute.return_value = Result.success(response)
            presenter.present_project.return_value = view_model

            result = controller.handle_create("プロジェクト", "説明")

            assert (
                result.success,
                create_use_case.execute.call_args,
                presenter.present_project.call_args,
            ) == (
                view_model,
                call(CreateProjectRequest(name="プロジェクト", description="説明")),
                call(response),
            )

        def test_ユースケースの失敗を表示モデルに変換する(
            self, fixture_controller: tuple[ProjectController, Mock, Mock]
        ) -> None:
            """ユースケースのエラーを表示モデルに変換して返すことを確認する."""
            controller, create_use_case, presenter = fixture_controller
            error = Error.validation_error("入力が不正です")
            error_view_model = ErrorViewModel(
                message="入力が不正です", code="VALIDATION_ERROR"
            )
            create_use_case.execute.return_value = Result.failure(error)
            presenter.present_error.return_value = error_view_model

            result = controller.handle_create("プロジェクト", "説明")

            assert (
                result.error,
                presenter.present_error.call_args,
            ) == (
                error_view_model,
                call("入力が不正です", "VALIDATION_ERROR"),
            )

        def test_value_errorを検証エラーに変換する(
            self, fixture_controller: tuple[ProjectController, Mock, Mock]
        ) -> None:
            """ValueErrorを検証エラーとして返すことを確認する."""
            controller, create_use_case, presenter = fixture_controller
            create_use_case.execute.side_effect = ValueError("入力値が不正です")
            error_view_model = ErrorViewModel(
                message="入力値が不正です", code="VALIDATION_ERROR"
            )
            presenter.present_error.return_value = error_view_model

            result = controller.handle_create("プロジェクト", "説明")

            assert (
                result.error,
                presenter.present_error.call_args,
            ) == (
                error_view_model,
                call("入力値が不正です", "VALIDATION_ERROR"),
            )
