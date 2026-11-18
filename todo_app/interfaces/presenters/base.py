# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""プレゼンタ基底モジュール."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from todo_app.application.dtos.project_dto import (
        CompleteProjectResponse,
        ProjectResponse,
    )
    from todo_app.application.dtos.task_dto import TaskResponse
    from todo_app.interfaces.view_models.base import ErrorViewModel
    from todo_app.interfaces.view_models.project_vm import (
        ProjectCompletionViewModel,
        ProjectViewModel,
    )
    from todo_app.interfaces.view_models.task_vm import TaskViewModel


class TaskPresenter(ABC):
    """タスク関係出力の基底クラス."""

    @abstractmethod
    def present_task(self, task_response: TaskResponse) -> TaskViewModel:
        """TaskResponseをTaskViewModelに変換するための抽象メソッド.

        Args:
            task_response (TaskResponse): タスクのレスポンスオブジェクト

        Returns:
            TaskViewModel: タスクのビュー モデル

        """
        raise NotImplementedError

    @abstractmethod
    def present_error(self, error_msg: str, code: str | None = None) -> ErrorViewModel:
        """エラー情報をErrorViewModelに変換するための抽象メソッド.

        Args:
            error_msg (str): エラーメッセージ
            code (str | None): エラーコード

        Returns:
            ErrorViewModel: エラー情報

        """
        raise NotImplementedError


class ProjectPresenter(ABC):
    """プロジェクト関係出力の基底クラス."""

    @abstractmethod
    def present_project(self, project_response: ProjectResponse) -> ProjectViewModel:
        """ProjectResponseをProjectViewModelに変換するための抽象メソッド.

        Args:
            project_response (ProjectResponse): プロジェクトのレスポンスオブジェクト

        Returns:
            ProjectViewModel: プロジェクトのビュー モデル

        """
        raise NotImplementedError

    @abstractmethod
    def present_complete(
        self, project_response: CompleteProjectResponse
    ) -> ProjectCompletionViewModel:
        """CompleteProjectResponseをProjectCompletionViewModelに変換するための抽象メソッド.

        Args:
            project_response (CompleteProjectResponse): 完了したプロジェクトの
                レスポンスオブジェクト

        Returns:
            ProjectCompletionViewModel: プロジェクト完了のビュー モデル

        """
        raise NotImplementedError

    @abstractmethod
    def present_error(self, error_msg: str, code: str | None = None) -> ErrorViewModel:
        """エラー情報をErrorViewModelに変換するための抽象メソッド.

        Args:
            error_msg (str): エラーメッセージ
            code (str | None): エラーコード

        Returns:
            ErrorViewModel: エラー情報

        """
        raise NotImplementedError
