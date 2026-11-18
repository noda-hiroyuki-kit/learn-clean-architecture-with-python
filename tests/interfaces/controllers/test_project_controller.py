# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""ProjectControllerのテスト."""

from datetime import UTC, datetime
from unittest.mock import Mock, call

import pytest

from todo_app.application.common.result import Error, Result
from todo_app.application.dtos.project_dto import (
    CompleteProjectRequest,
    CompleteProjectResponse,
    CreateProjectRequest,
    ProjectResponse,
    UpdateProjectRequest,
)
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
from todo_app.interfaces.view_models.project_vm import (
    ProjectCompletionViewModel,
    ProjectViewModel,
)


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

    class TestHandleComplete:
        """handle_completeのテスト."""

        @pytest.fixture
        def fixture_controller(self) -> tuple[ProjectController, Mock, Mock]:
            """テスト用のProjectControllerを生成する."""
            complete_use_case = Mock(spec=CompleteProjectUseCase)
            presenter = Mock(spec=ProjectPresenter)
            controller = ProjectController(
                create_use_case=Mock(spec=CreateProjectUseCase),
                complete_use_case=complete_use_case,
                presenter=presenter,
                get_use_case=Mock(spec=GetProjectUseCase),
                list_use_case=Mock(spec=ListProjectsUseCase),
                update_use_case=Mock(spec=UpdateProjectUseCase),
            )
            return controller, complete_use_case, presenter

        def test_完了成功時に完了表示モデルを返す(
            self, fixture_controller: tuple[ProjectController, Mock, Mock]
        ) -> None:
            """完了結果を完了表示モデルに変換して返すことを確認する."""
            controller, complete_use_case, presenter = fixture_controller
            project_id = "12345678-1234-5678-1234-567812345678"
            response = CompleteProjectResponse(
                id=project_id,
                status="COMPLETED",
                completion_date=datetime(2026, 1, 1, tzinfo=UTC),
                task_count=2,
                completion_notes="完了メモ",
            )
            view_model = ProjectCompletionViewModel(
                project_id=project_id,
                completion_notes="完了メモ",
            )
            complete_use_case.execute.return_value = Result.success(response)
            presenter.present_complete.return_value = view_model

            result = controller.handle_complete(project_id, "完了メモ")

            assert (
                result.success,
                complete_use_case.execute.call_args,
                presenter.present_complete.call_args,
            ) == (
                view_model,
                call(
                    CompleteProjectRequest(
                        project_id=project_id, completion_notes="完了メモ"
                    )
                ),
                call(response),
            )

        def test_ユースケースの失敗を表示モデルに変換する(
            self, fixture_controller: tuple[ProjectController, Mock, Mock]
        ) -> None:
            """ユースケースのエラーを表示モデルに変換して返すことを確認する."""
            controller, complete_use_case, presenter = fixture_controller
            project_id = "12345678-1234-5678-1234-567812345678"
            error = Error.not_found("Project", project_id)
            error_view_model = ErrorViewModel(
                message=f"id {project_id} の Project が見つかりません",
                code="NOT_FOUND",
            )
            complete_use_case.execute.return_value = Result.failure(error)
            presenter.present_error.return_value = error_view_model

            result = controller.handle_complete(project_id)

            assert (
                result.error,
                presenter.present_error.call_args,
            ) == (
                error_view_model,
                call(f"id {project_id} の Project が見つかりません", "NOT_FOUND"),
            )

        def test_value_errorを検証エラーに変換する(
            self, fixture_controller: tuple[ProjectController, Mock, Mock]
        ) -> None:
            """ValueErrorを検証エラーとして返すことを確認する."""
            controller, complete_use_case, presenter = fixture_controller
            complete_use_case.execute.side_effect = ValueError(
                "プロジェクト ID の形式が無効です"
            )
            error_view_model = ErrorViewModel(
                message="プロジェクト ID の形式が無効です",
                code="VALIDATION_ERROR",
            )
            presenter.present_error.return_value = error_view_model

            result = controller.handle_complete("invalid-project-id")

            assert (
                result.error,
                presenter.present_error.call_args,
            ) == (
                error_view_model,
                call("プロジェクト ID の形式が無効です", "VALIDATION_ERROR"),
            )

    class TestHandleGet:
        """handle_getのテスト."""

        @pytest.fixture
        def fixture_controller(self) -> tuple[ProjectController, Mock, Mock]:
            """テスト用のProjectControllerを生成する."""
            get_use_case = Mock(spec=GetProjectUseCase)
            presenter = Mock(spec=ProjectPresenter)
            controller = ProjectController(
                create_use_case=Mock(spec=CreateProjectUseCase),
                complete_use_case=Mock(spec=CompleteProjectUseCase),
                presenter=presenter,
                get_use_case=get_use_case,
                list_use_case=Mock(spec=ListProjectsUseCase),
                update_use_case=Mock(spec=UpdateProjectUseCase),
            )
            return controller, get_use_case, presenter

        def test_取得成功時に表示モデルを返す(
            self, fixture_controller: tuple[ProjectController, Mock, Mock]
        ) -> None:
            """取得結果を表示モデルに変換して返すことを確認する."""
            controller, get_use_case, presenter = fixture_controller
            project_id = "12345678-1234-5678-1234-567812345678"
            response = ProjectResponse(
                id=project_id,
                name="プロジェクト",
                description="説明",
                status="ACTIVE",
                completion_date=None,
                tasks=[],
            )
            view_model = ProjectViewModel(
                id=project_id,
                name="プロジェクト",
                description="説明",
                project_type="通常",
                status_display="進行中",
                task_count=0,
                completed_task_count=0,
                completion_info=None,
                tasks=[],
            )
            get_use_case.execute.return_value = Result.success(response)
            presenter.present_project.return_value = view_model

            result = controller.handle_get(project_id)

            assert (
                result.success,
                get_use_case.execute.call_args,
                presenter.present_project.call_args,
            ) == (
                view_model,
                call(project_id),
                call(response),
            )

        def test_ユースケースの失敗を表示モデルに変換する(
            self, fixture_controller: tuple[ProjectController, Mock, Mock]
        ) -> None:
            """ユースケースのエラーを表示モデルに変換して返すことを確認する."""
            controller, get_use_case, presenter = fixture_controller
            project_id = "12345678-1234-5678-1234-567812345678"
            error = Error.not_found("Project", project_id)
            error_view_model = ErrorViewModel(
                message=f"id {project_id} の Project が見つかりません",
                code="NOT_FOUND",
            )
            get_use_case.execute.return_value = Result.failure(error)
            presenter.present_error.return_value = error_view_model

            result = controller.handle_get(project_id)

            assert (
                result.error,
                presenter.present_error.call_args,
            ) == (
                error_view_model,
                call(f"id {project_id} の Project が見つかりません", "NOT_FOUND"),
            )

        def test_value_errorを検証エラーに変換する(
            self, fixture_controller: tuple[ProjectController, Mock, Mock]
        ) -> None:
            """ValueErrorを検証エラーとして返すことを確認する."""
            controller, get_use_case, presenter = fixture_controller
            get_use_case.execute.side_effect = ValueError("プロジェクト ID が不正です")
            error_view_model = ErrorViewModel(
                message="プロジェクト ID が不正です", code="VALIDATION_ERROR"
            )
            presenter.present_error.return_value = error_view_model

            result = controller.handle_get("invalid-project-id")

            assert (
                result.error,
                presenter.present_error.call_args,
            ) == (
                error_view_model,
                call("プロジェクト ID が不正です", "VALIDATION_ERROR"),
            )

    class TestHandleList:
        """handle_listのテスト."""

        @pytest.fixture
        def fixture_controller(self) -> tuple[ProjectController, Mock, Mock]:
            """テスト用のProjectControllerを生成する."""
            list_use_case = Mock(spec=ListProjectsUseCase)
            presenter = Mock(spec=ProjectPresenter)
            controller = ProjectController(
                create_use_case=Mock(spec=CreateProjectUseCase),
                complete_use_case=Mock(spec=CompleteProjectUseCase),
                presenter=presenter,
                get_use_case=Mock(spec=GetProjectUseCase),
                list_use_case=list_use_case,
                update_use_case=Mock(spec=UpdateProjectUseCase),
            )
            return controller, list_use_case, presenter

        def test_取得成功時に表示モデルの一覧を返す(
            self, fixture_controller: tuple[ProjectController, Mock, Mock]
        ) -> None:
            """一覧の各取得結果を表示モデルに変換して返すことを確認する."""
            controller, list_use_case, presenter = fixture_controller
            responses = [
                ProjectResponse(
                    id="project-1",
                    name="プロジェクト1",
                    description="説明1",
                    status="ACTIVE",
                    completion_date=None,
                    tasks=[],
                ),
                ProjectResponse(
                    id="project-2",
                    name="プロジェクト2",
                    description="説明2",
                    status="ACTIVE",
                    completion_date=None,
                    tasks=[],
                ),
            ]
            view_models = [
                ProjectViewModel(
                    id="project-1",
                    name="プロジェクト1",
                    description="説明1",
                    project_type="通常",
                    status_display="進行中",
                    task_count=0,
                    completed_task_count=0,
                    completion_info=None,
                    tasks=[],
                ),
                ProjectViewModel(
                    id="project-2",
                    name="プロジェクト2",
                    description="説明2",
                    project_type="通常",
                    status_display="進行中",
                    task_count=0,
                    completed_task_count=0,
                    completion_info=None,
                    tasks=[],
                ),
            ]
            list_use_case.execute.return_value = Result.success(responses)
            presenter.present_project.side_effect = view_models

            result = controller.handle_list()

            assert (
                result.success,
                list_use_case.execute.call_args,
                presenter.present_project.call_args_list,
            ) == (
                view_models,
                call(),
                [call(response) for response in responses],
            )

        def test_ユースケースの失敗を表示モデルに変換する(
            self, fixture_controller: tuple[ProjectController, Mock, Mock]
        ) -> None:
            """ユースケースのエラーを表示モデルに変換して返すことを確認する."""
            controller, list_use_case, presenter = fixture_controller
            error = Error.business_rule_violation("プロジェクト一覧を取得できません")
            error_view_model = ErrorViewModel(
                message="プロジェクト一覧を取得できません",
                code="BUSINESS_RULE_VIOLATION",
            )
            list_use_case.execute.return_value = Result.failure(error)
            presenter.present_error.return_value = error_view_model

            result = controller.handle_list()

            assert (
                result.error,
                list_use_case.execute.call_args,
                presenter.present_error.call_args,
            ) == (
                error_view_model,
                call(),
                call("プロジェクト一覧を取得できません", "BUSINESS_RULE_VIOLATION"),
            )

    class TestHandleUpdate:
        """handle_updateのテスト."""

        @pytest.fixture
        def fixture_controller(self) -> tuple[ProjectController, Mock, Mock]:
            """テスト用のProjectControllerを生成する."""
            update_use_case = Mock(spec=UpdateProjectUseCase)
            presenter = Mock(spec=ProjectPresenter)
            controller = ProjectController(
                create_use_case=Mock(spec=CreateProjectUseCase),
                complete_use_case=Mock(spec=CompleteProjectUseCase),
                presenter=presenter,
                get_use_case=Mock(spec=GetProjectUseCase),
                list_use_case=Mock(spec=ListProjectsUseCase),
                update_use_case=update_use_case,
            )
            return controller, update_use_case, presenter

        def test_更新成功時に表示モデルを返す(
            self, fixture_controller: tuple[ProjectController, Mock, Mock]
        ) -> None:
            """更新結果を表示モデルに変換して返すことを確認する."""
            controller, update_use_case, presenter = fixture_controller
            project_id = "12345678-1234-5678-1234-567812345678"
            response = ProjectResponse(
                id=project_id,
                name="更新後のプロジェクト",
                description="更新後の説明",
                status="ACTIVE",
                completion_date=None,
                tasks=[],
            )
            view_model = ProjectViewModel(
                id=project_id,
                name="更新後のプロジェクト",
                description="更新後の説明",
                project_type="通常",
                status_display="進行中",
                task_count=0,
                completed_task_count=0,
                completion_info=None,
                tasks=[],
            )
            update_use_case.execute.return_value = Result.success(response)
            presenter.present_project.return_value = view_model

            result = controller.handle_update(
                project_id, "更新後のプロジェクト", "更新後の説明"
            )

            assert (
                result.success,
                update_use_case.execute.call_args,
                presenter.present_project.call_args,
            ) == (
                view_model,
                call(
                    UpdateProjectRequest(
                        project_id=project_id,
                        name="更新後のプロジェクト",
                        description="更新後の説明",
                    )
                ),
                call(response),
            )

        def test_ユースケースの失敗を表示モデルに変換する(
            self, fixture_controller: tuple[ProjectController, Mock, Mock]
        ) -> None:
            """ユースケースのエラーを表示モデルに変換して返すことを確認する."""
            controller, update_use_case, presenter = fixture_controller
            project_id = "12345678-1234-5678-1234-567812345678"
            error = Error.not_found("Project", project_id)
            error_view_model = ErrorViewModel(
                message=f"id {project_id} の Project が見つかりません",
                code="NOT_FOUND",
            )
            update_use_case.execute.return_value = Result.failure(error)
            presenter.present_error.return_value = error_view_model

            result = controller.handle_update(project_id, name="更新名")

            assert (
                result.error,
                presenter.present_error.call_args,
            ) == (
                error_view_model,
                call(f"id {project_id} の Project が見つかりません", "NOT_FOUND"),
            )

        def test_value_errorを検証エラーに変換する(
            self, fixture_controller: tuple[ProjectController, Mock, Mock]
        ) -> None:
            """ValueErrorを検証エラーとして返すことを確認する."""
            controller, update_use_case, presenter = fixture_controller
            update_use_case.execute.side_effect = ValueError(
                "プロジェクト ID の形式が無効です"
            )
            error_view_model = ErrorViewModel(
                message="プロジェクト ID の形式が無効です",
                code="VALIDATION_ERROR",
            )
            presenter.present_error.return_value = error_view_model

            result = controller.handle_update("invalid-project-id", name="更新名")

            assert (
                result.error,
                presenter.present_error.call_args,
            ) == (
                error_view_model,
                call("プロジェクト ID の形式が無効です", "VALIDATION_ERROR"),
            )
