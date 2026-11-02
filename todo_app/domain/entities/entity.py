# https://github.com/PacktPublishing/Clean-Architecture-with-Python
# SPDX-License-Identifier: MIT
# MIT License
# Copyright (c) 2024 Packt
# Copyright (c) 2026 Noda Hiroyuki.
"""ドメインエンティティの基底クラス."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Entity:
    """ドメインエンティティの基底クラス."""

    id: UUID = field(default_factory=uuid4, init=False)

    def __eq__(self, other: object) -> bool:
        """エンティティidが等しいかどうかを比較する."""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """エンティティidに基づいてハッシュ値を計算する."""
        return hash(self.id)
