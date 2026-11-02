# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""Taskエンティティ."""

from dataclasses import dataclass

from .entity import Entity


@dataclass
class Task(Entity):
    """Taskエンティティ."""

    title: str
