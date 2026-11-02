# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""Value Objectモジュール."""

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
