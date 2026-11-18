# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""タスク関係のコントローラ モジュール."""

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from todo_app.application.dtos.task_dto import UpdateTaskRequest
from todo_app.application.use_cases.task_use_cases import (
    CompleteTaskRequest,
    CompleteTaskUseCase,
    CreateTaskRequest,
    CreateTaskUseCase,
    GetTaskUseCase,
    UpdateTaskUseCase,
)
from todo_app.domain.value_object import Priority, TaskStatus
from todo_app.interfaces.view_models.base import OperationResult

if TYPE_CHECKING:
    from todo_app.interfaces.presenters.base import TaskPresenter
    from todo_app.interfaces.view_models.task_vm import TaskViewModel


@dataclass
class TaskController:
    """タスク関係のコントローラ."""

    create_use_case: CreateTaskUseCase
    get_use_case: GetTaskUseCase
    complete_use_case: CompleteTaskUseCase
    update_use_case: UpdateTaskUseCase
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

    def handle_get(self, task_id: str) -> OperationResult[TaskViewModel]:
        """タスク取得のリクエストを処理する.

        Args:
            task_id (str): タスクのID

        Returns:
            OperationResult[TaskViewModel]: タスク取得の結果

        """
        try:
            result = self.get_use_case.execute(UUID(task_id))
            if result.is_success:
                view_model = self.presenter.present_task(result.value)
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_complete(
        self, task_id: str, notes: str | None = None
    ) -> OperationResult[TaskViewModel]:
        """タスク完了のリクエストを処理する.

        Args:
            task_id (str): タスクのID
            notes (str | None): 完了時のメモ

        Returns:
            OperationResult[TaskViewModel]: タスク完了の結果

        """
        try:
            request = CompleteTaskRequest(task_id=task_id, completion_notes=notes)
            result = self.complete_use_case.execute(request)

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

    def handle_update(
        self,
        task_id: str,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        priority: str | None = None,
    ) -> OperationResult[TaskViewModel]:
        """タスク更新のリクエストを処理する.

        Args:
            task_id (str): タスクのID
            title (str | None): タイトル
            description (str | None): 説明
            status (str | None): ステータス
            priority (str | None): 優先度

        Returns:
            OperationResult[TaskViewModel]: タスク更新の結果

        """
        try:
            # Convert string status/priority to enums if provided
            status_enum = TaskStatus[status.upper()] if status else None
            priority_enum = Priority[priority.upper()] if priority else None

            request = UpdateTaskRequest(
                task_id=task_id,
                title=title,
                description=description,
                status=status_enum,
                priority=priority_enum,
            )
            result = self.update_use_case.execute(request)
            if result.is_success:
                view_model = self.presenter.present_task(result.value)
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        except (ValueError, KeyError) as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)
