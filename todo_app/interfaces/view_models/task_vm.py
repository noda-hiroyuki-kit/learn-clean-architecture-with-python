# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""タスクのビュー モデル モジュール."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskViewModel:
    """タスクのビュー モデル."""

    id: str
    title: str
    description: str
    status_display: str  # 人が読める status
    priority_display: str  # 人が読める priority
    due_date_display: str | None  # フォーマット済み日付文字列
    project_display: str | None  # プロジェクト名(存在する場合)
    completion_info: str | None  # フォーマット済み完了情報
