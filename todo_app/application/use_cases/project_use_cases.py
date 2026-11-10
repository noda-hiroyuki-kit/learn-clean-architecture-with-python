# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""Projectに関連するユースケースを定義するモジュール."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from todo_app.application.common.result import Error, Result
from todo_app.application.dtos.project_dto import (
    CompleteProjectResponse,
    ProjectResponse,
)
from todo_app.application.repositories.project_repository import ProjectRepository
from todo_app.application.repositories.task_repository import TaskRepository
from todo_app.application.service_ports.notifications import NotificationPort
from todo_app.domain.entities.project import Project
from todo_app.domain.exceptions import (
    BusinessRuleViolationError,
    ProjectNotFoundError,
    ValidationError,
)

if TYPE_CHECKING:
    from todo_app.application.dtos.project_dto import (
        CompleteProjectRequest,
        CreateProjectRequest,
    )
    from todo_app.application.repositories.project_repository import ProjectRepository
    from todo_app.application.repositories.task_repository import TaskRepository
    from todo_app.application.service_ports.notifications import (
        NotificationPort,
    )


@dataclass
class CreateProjectUseCase:
    """プロジェクトを作成するユースケース."""

    project_repository: ProjectRepository

    def execute(self, request: CreateProjectRequest) -> Result:
        """プロジェクトを作成する.

        Parameters
        ----------
        request : CreateProjectRequest
            プロジェクト作成リクエスト.

        Returns
        -------
        Result
            ユースケースの実行結果.

        """
        try:
            params = request.to_execution_params()
            project = Project(name=params["name"], description=params["description"])
            self.project_repository.save(project)

            return Result.success(ProjectResponse.from_entity(project))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolationError as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass(frozen=True)
class CompleteProjectUseCase:
    """プロジェクトを完了するユースケース."""

    project_repository: ProjectRepository
    task_repository: TaskRepository
    notification_service: NotificationPort

    def execute(self, request: CompleteProjectRequest) -> Result:
        """プロジェクトを完了する.

        Parameters
        ----------
        request : CompleteProjectRequest
            プロジェクト完了リクエスト.

        Returns
        -------
        Result
            ユースケースの実行結果.

        """
        try:
            params = request.to_execution_params()

            # Validate project exists
            project = self.project_repository.get(params["project_id"])
            project.mark_completed(notes=params["completion_notes"])

            # 未完了タスクをすべて完了にする
            for task in project.incomplete_tasks:
                task.complete()
                self.task_repository.save(task)
                self.notification_service.notify_task_completed(task)

            # Complete the project itself
            project.mark_completed(notes=params["completion_notes"])
            self.project_repository.save(project)
            response = CompleteProjectResponse.from_entity(project)
            return Result.success(response)

        except ProjectNotFoundError:
            return Result.failure(Error.not_found("Project", str(params["project_id"])))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
