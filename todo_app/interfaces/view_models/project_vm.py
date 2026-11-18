# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""プロジェクトのViewModelモジュール."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from todo_app.interfaces.view_models.task_vm import TaskViewModel


@dataclass(frozen=True)
class ProjectViewModel:
    """プロジェクトのViewModel."""

    id: str
    name: str
    description: str
    project_type: str
    status_display: str
    task_count: int
    completed_task_count: int
    completion_info: str | None
    tasks: list[TaskViewModel]


@dataclass(frozen=True)
class ProjectCompletionViewModel:
    """プロジェクト完了のViewModel."""

    project_id: str
    completion_notes: str | None
