# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""操作結果DTOのテスト."""

from uuid import UUID

from todo_app.application.dtos.operations import DeletionOutcome


class TestDeletionOutcome:
    """DeletionOutcomeのテスト."""

    def test文字列化で削除結果を説明する(self) -> None:
        """削除対象のIDを含む文字列表現を返すことを確認する."""
        entity_id = UUID("12345678-1234-5678-1234-567812345678")
        outcome = DeletionOutcome(entity_id)

        assert str(outcome) == (f"ID: {entity_id} のエンティティを正常に削除しました。")
