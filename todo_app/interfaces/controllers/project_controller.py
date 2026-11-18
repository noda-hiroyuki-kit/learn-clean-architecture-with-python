# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""プロジェクトコントローラモジュール."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from todo_app.application.dtos.project_dto import (
    CompleteProjectRequest,
    CreateProjectRequest,
    UpdateProjectRequest,
)
from todo_app.interfaces.view_models.base import OperationResult

if TYPE_CHECKING:
    from todo_app.application.use_cases.project_use_cases import (
        CompleteProjectUseCase,
        CreateProjectUseCase,
        GetProjectUseCase,
        ListProjectsUseCase,
        UpdateProjectUseCase,
    )
    from todo_app.interfaces.presenters.base import ProjectPresenter
    from todo_app.interfaces.view_models.project_vm import ProjectViewModel


@dataclass
class ProjectController:
    """プロジェクトコントローラ."""

    create_use_case: CreateProjectUseCase
    complete_use_case: CompleteProjectUseCase
    presenter: ProjectPresenter
    get_use_case: GetProjectUseCase
    list_use_case: ListProjectsUseCase
    update_use_case: UpdateProjectUseCase

    def handle_create(self, name: str, description: str = "") -> OperationResult:
        """プロジェクト作成のハンドラ.

        Args:
            name (str): プロジェクト名
            description (str, optional): プロジェクトの説明. Defaults to "".

        Returns:
            OperationResult: 操作結果

        """
        try:
            request = CreateProjectRequest(name=name, description=description)
            result = self.create_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_project(result.value)
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_complete(
        self, project_id: str, notes: str | None = None
    ) -> OperationResult:
        """プロジェクト完了のハンドラ.

        Args:
            project_id (str): プロジェクトID
            notes (str | None, optional): 完了時のメモ. Defaults to None.

        Returns:
            OperationResult: 操作結果

        """
        try:
            request = CompleteProjectRequest(
                project_id=project_id, completion_notes=notes
            )
            result = self.complete_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_complete(result.value)
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_get(self, project_id: str) -> OperationResult[ProjectViewModel]:
        """プロジェクト取得のハンドラ.

        Args:
            project_id (str): プロジェクトID

        Returns:
            OperationResult[ProjectViewModel]: 操作結果

        """
        try:
            result = self.get_use_case.execute(project_id)

            if result.is_success:
                view_model = self.presenter.present_project(result.value)
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_list(self) -> OperationResult[list[ProjectViewModel]]:
        """プロジェクト一覧取得のハンドラ.

        Returns:
            OperationResult[list[ProjectViewModel]]: 操作結果

        """
        result = self.list_use_case.execute()

        if result.is_success:
            view_models = [
                self.presenter.present_project(proj) for proj in result.value
            ]
            return OperationResult.succeed(view_models)

        error_vm = self.presenter.present_error(
            result.error.message, str(result.error.code.name)
        )
        return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_update(
        self, project_id: str, name: str | None = None, description: str | None = None
    ) -> OperationResult[ProjectViewModel]:
        """プロジェクト更新のハンドラ.

        Args:
            project_id (str): プロジェクトID
            name (str|None, optional): プロジェクト名. Defaults to None.
            description (str|None, optional): プロジェクト説明. Defaults to None.

        Returns:
            OperationResult[ProjectViewModel]: 操作結果

        """
        try:
            request = UpdateProjectRequest(
                project_id=project_id, name=name, description=description
            )
            result = self.update_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_project(result.value)
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)
