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

    dummy: int
