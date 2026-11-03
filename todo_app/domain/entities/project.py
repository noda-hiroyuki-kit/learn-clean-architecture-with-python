# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.

"""Projectエンティティ."""

from dataclasses import dataclass

from todo_app.domain.entities.entity import Entity


@dataclass
class Project(Entity):
    """Projectエンティティ."""

    name: str
