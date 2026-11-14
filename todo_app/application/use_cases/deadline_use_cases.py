# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""期限チェックユースケース."""

from dataclasses import dataclass, field
from datetime import timedelta
from typing import TYPE_CHECKING

from todo_app.application.common.result import Error, Result
from todo_app.domain.exceptions import (
    BusinessRuleViolationError,
    TaskNotFoundError,
    ValidationError,
)

if TYPE_CHECKING:
    from todo_app.application.repositories.task_repository import TaskRepository
    from todo_app.application.service_ports.notifications import NotificationPort


@dataclass
class CheckDeadlinesUseCase:
    """期限チェックユースケース."""

    task_repository: TaskRepository
    notification_service: NotificationPort
    warning_threshold: timedelta = field(default=timedelta(days=1))

    def execute(self) -> Result:
        """全てのタスクをチェックし、期限が近いものに通知を送る."""
        try:
            tasks = self.task_repository.get_active_tasks()
            notifications_sent = 0

            for task in tasks:
                if task.due_date and task.due_date.is_approaching(
                    self.warning_threshold
                ):
                    remaining_days = int(
                        task.due_date.time_remaining().total_seconds() / (24 * 3600)
                    )
                    self.notification_service.notify_task_deadline_approaching(
                        task, remaining_days
                    )
                    notifications_sent += 1

            return Result.success({"notifications_sent": notifications_sent})

        except TaskNotFoundError as e:
            return Result.failure(Error.not_found("Task", str(e)))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolationError as e:
            return Result.failure(Error.business_rule_violation(str(e)))
