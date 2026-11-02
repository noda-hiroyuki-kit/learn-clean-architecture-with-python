# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""Value Objectモジュール."""

import datetime as dt
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """タスクの状態を表すValue Object."""

    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class Priority(Enum):
    """タスクの優先度を表すValue Object."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass(frozen=True)
class Deadline:
    """タスクの期限を表すValue Object."""

    due_date: dt.datetime

    def __post_init__(self) -> None:
        """期限がタイムゾーン情報を持っているか確認し、現在時刻以降であることを検証する."""
        if not self.due_date.tzinfo:
            msg = "期限にはタイムゾーン情報が必要です。"
            raise ValueError(msg)
        if self.due_date < dt.datetime.now(tz=dt.UTC):
            msg = "期限は現在時刻以降でなければなりません。"
            raise ValueError(msg)
