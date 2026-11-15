# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""タスク関係のコントローラ モジュール."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from todo_app.application.use_cases.task_use_cases import (
    CompleteTaskUseCase,
    CreateTaskRequest,
    CreateTaskUseCase,
)
from todo_app.interfaces.view_models.base import OperationResult

if TYPE_CHECKING:
    from todo_app.interfaces.presenters.base import TaskPresenter
    from todo_app.interfaces.view_models.task_vm import TaskViewModel


@dataclass
class TaskController:
    """タスク関係のコントローラ."""

    create_use_case: CreateTaskUseCase
    complete_use_case: CompleteTaskUseCase
    presenter: TaskPresenter

    def handle_create(
        self, title: str, description: str
    ) -> OperationResult[TaskViewModel]:
        """タスク作成のリクエストを処理する.

        Args:
            title (str): タスクのタイトル
            description (str): タスクの説明

        Returns:
            OperationResult[TaskViewModel]: タスク作成の結果

        """
        try:
            request = CreateTaskRequest(title=title, description=description)
            result = self.create_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_task(result.value)
                return OperationResult.succeed(view_model)

            if result.error is not None:
                error_vm = self.presenter.present_error(
                    result.error.message, str(result.error.code.name)
                )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)
