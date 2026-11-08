# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""Projectに関連するユースケースを定義するモジュール."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from todo_app.application.common.result import Error, Result
from todo_app.application.repositories.project_repository import ProjectRepository
from todo_app.application.repositories.task_repository import TaskRepository
from todo_app.application.service_ports.notifications import NotificationPort
from todo_app.domain.exceptions import ProjectNotFoundError, ValidationError

if TYPE_CHECKING:
    from todo_app.application.dtos.project_dto import CompleteProjectRequest
    from todo_app.application.repositories.project_repository import ProjectRepository
    from todo_app.application.repositories.task_repository import TaskRepository
    from todo_app.application.service_ports.notifications import (
        NotificationPort,
    )


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

            # Complete all outstanding tasks
            for task in project.incomplete_tasks:
                task.complete()
                self.task_repository.save(task)
                self.notification_service.notify_task_completed(task)

            # Complete the project itself
            project.mark_completed(notes=params["completion_notes"])
            self.project_repository.save(project)

            return Result.success(
                {
                    "id": str(project.id),
                    "status": project.status,
                    "completion_date": project.completed_at,
                    "task_count": len(project.tasks),
                    "completion_notes": project.completion_notes,
                }
            )

        except ProjectNotFoundError:
            return Result.failure(Error.not_found("Project", request.project_id))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
