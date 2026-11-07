# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""タスクドメインで使用する値オブジェクトを定義するモジュール."""

import datetime as dt
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """タスクの進行状態を表す列挙型."""

    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class ProjectStatus(Enum):
    """プロジェクトの進行状態を表す列挙型."""

    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


class Priority(Enum):
    """タスクの優先度を表す列挙型."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass(frozen=True)
class Deadline:
    """タイムゾーン付きのタスク期限を表す不変の値オブジェクト."""

    due_date: dt.datetime

    def __post_init__(self) -> None:
        """期限にタイムゾーン情報があり、現在時刻以降であることを検証する."""
        if not self.due_date.tzinfo:
            msg = "期限にはタイムゾーン情報が必要です。"
            raise ValueError(msg)
        if self.due_date < dt.datetime.now(tz=dt.UTC):
            msg = "期限は現在時刻以降でなければなりません。"
            raise ValueError(msg)

    def is_overdue(self) -> bool:
        """現在時刻が期限を過ぎている場合はTrueを返す."""
        return dt.datetime.now(tz=dt.UTC) > self.due_date

    def time_remaining(self) -> dt.timedelta:
        """期限までの残り時間を返し、期限後はゼロを返す."""
        return max(dt.timedelta(0), self.due_date - dt.datetime.now(tz=dt.UTC))

    def is_approaching(
        self,
        warning_threshold: dt.timedelta = dt.timedelta(days=1),
    ) -> bool:
        """期限までの残り時間が正かつ指定したしきい値以内の場合にTrueを返す."""
        return dt.timedelta(0) < self.time_remaining() <= warning_threshold
