# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""Taskエンティティ."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .entity import Entity
from .value_object import Priority

if TYPE_CHECKING:
    from uuid import UUID


@dataclass
class Task(Entity):
    """Taskエンティティ."""

    title: str
    description: str
    project_id: UUID
    priority: Priority = Priority.MEDIUM
