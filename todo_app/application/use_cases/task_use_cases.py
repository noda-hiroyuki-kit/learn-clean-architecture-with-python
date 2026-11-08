# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""Taskに関連するユースケースを定義するモジュール."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from todo_app.application.common.result import Error, Result
from todo_app.application.dtos.task_dto import TaskResponse
from todo_app.domain.exceptions import (
    TaskNotFoundError,
    ValidationError,
)
from todo_app.domain.value_object import Priority

if TYPE_CHECKING:
    import datetime as dt
    from uuid import UUID

    from todo_app.application.dtos.task_dto import SetTaskPriorityRequest
    from todo_app.application.repositories.task_repository import TaskRepository
    from todo_app.application.service_ports.notifications import NotificationPort
    from todo_app.domain.entities.task import Task


def _get_completed_at(task: Task) -> dt.datetime:
    """完了済みTaskの完了時刻を取得する.

    Parameters
    ----------
    task : Task
        完了時刻を取得するTaskエンティティ.

    Returns
    -------
    dt.datetime
        Taskの完了時刻.

    Raises
    ------
    ValueError
        completed_atがNoneの場合.

    """
    if task.completed_at is None:
        msg = "完了したTaskにcompleted_atが設定されていません。"
        raise ValueError(msg)
    return task.completed_at


@dataclass
class CompleteTaskUseCase:
    """Taskを完了にし、関係者に通知するユースケース."""

    task_repository: TaskRepository

    def execute(
        self,
        task_id: UUID,
        completion_notes: str | None = None,
    ) -> Result:
        """taskを完了するユースケースを実行する."""
        try:
            # Input validation
            task = self.task_repository.get(task_id)
            task.complete(notes=completion_notes)
            self.task_repository.save(task)

            # Return simplified task data
            return Result.success(
                {
                    "id": str(task.id),
                    "status": "completed",
                    "completion_date": _get_completed_at(task).isoformat(),
                }
            )

        except TaskNotFoundError:
            return Result.failure(Error.not_found("Task", str(task_id)))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))


@dataclass
class SetTaskPriorityUseCase:
    """Taskの優先度を設定するユースケース."""

    task_repository: TaskRepository
    notification_service: NotificationPort  # Depends on capability interface

    def execute(self, request: SetTaskPriorityRequest) -> Result:
        """Taskの優先度を設定するユースケースを実行する."""
        try:
            params = request.to_execution_params()

            task = self.task_repository.get(params["task_id"])
            task.priority = params["priority"]

            self.task_repository.save(task)

            if task.priority == Priority.HIGH:
                self.notification_service.notify_task_high_priority(task)

            return Result.success(TaskResponse.from_entity(task))
        except TaskNotFoundError:
            return Result.failure(Error.not_found("Task", str(params["task_id"])))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
