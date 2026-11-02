# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""Tests for the domain entity base class."""

from dataclasses import dataclass
from uuid import UUID, uuid4

import pytest

from todo_app.domain.entities.entity import Entity


@dataclass(eq=False)
class ConcreteEntity(Entity):
    """テスト用の具象エンティティ."""


@dataclass(eq=False)
class AnotherEntity(Entity):
    """型比較テスト用の別エンティティ."""


class TestEntity:
    """Entity基底クラスのテスト."""

    def test_idが自動生成される(self) -> None:
        """生成時にUUIDのidが自動で割り当てられる."""
        entity = ConcreteEntity()

        assert isinstance(entity.id, UUID)

    def test_idはエンティティごとに一意である(self) -> None:
        """エンティティごとに異なるidが割り当てられる."""
        entity1 = ConcreteEntity()
        entity2 = ConcreteEntity()

        assert entity1.id != entity2.id

    def test_同一idのエンティティは等しい(self) -> None:
        """同じidを持つ同型のエンティティは等しいと判定される."""
        entity1 = ConcreteEntity()
        entity2 = ConcreteEntity()
        entity2.id = entity1.id

        assert entity1 == entity2

    def test_異なるidのエンティティは等しくない(self) -> None:
        """異なるidを持つエンティティは等しくないと判定される."""
        entity1 = ConcreteEntity()
        entity2 = ConcreteEntity()

        assert entity1 != entity2

    def test_異なる型のエンティティとは等しくない(self) -> None:
        """idが同じでも型が異なる場合は等しくないと判定される."""
        entity = ConcreteEntity()
        other = AnotherEntity()
        other.id = entity.id

        assert entity != other

    def test_文字列とは等しくない(self) -> None:
        """文字列との比較はFalseになる."""
        entity = ConcreteEntity()

        assert entity != "not an entity"

    def test_idとは等しくない(self) -> None:
        """UUIDとの比較はFalseになる."""
        entity = ConcreteEntity()

        assert entity != entity.id

    def test_同一idのエンティティはハッシュ値が等しい(self) -> None:
        """同じidを持つエンティティは同じハッシュ値を返す."""
        entity1 = ConcreteEntity()
        entity2 = ConcreteEntity()
        entity2.id = entity1.id

        assert hash(entity1) == hash(entity2)

    def test_ハッシュ値はidに基づく(self) -> None:
        """ハッシュ値はidのハッシュ値と一致する."""
        entity = ConcreteEntity()

        assert hash(entity) == hash(entity.id)

    def test_セットで同一エンティティは重複しない(self) -> None:
        """同じidのエンティティはセット内で1つにまとめられる."""
        entity1 = ConcreteEntity()
        entity2 = ConcreteEntity()
        entity2.id = entity1.id

        assert len({entity1, entity2}) == 1

    def test_idはコンストラクタで指定できない(self) -> None:
        """idはinit=Falseのためコンストラクタ引数に指定できない."""
        with pytest.raises(TypeError):
            ConcreteEntity(id=uuid4())  # type: ignore[call-arg]
