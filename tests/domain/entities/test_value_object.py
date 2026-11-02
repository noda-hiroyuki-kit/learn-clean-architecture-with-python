# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""Value Objectのテストモジュール."""

import datetime as dt

import pytest

from todo_app.domain.entities.value_object import Deadline


def test_deadlineにはタイムゾーン情報が必要であることを検証する_requires() -> None:
    """期限にタイムゾーン情報が必要であることを検証する."""
    with pytest.raises(ValueError, match="期限にはタイムゾーン情報が必要です。"):
        Deadline(due_date=dt.datetime(2024, 1, 1, 12, 0, 0))  # noqa: DTZ001


def test_deadlineは現在時刻以降であることを検証する_requires() -> None:
    """期限が現在時刻以降であることを検証する."""
    past_date = dt.datetime.now(tz=dt.UTC) - dt.timedelta(days=1)
    with pytest.raises(ValueError, match="期限は現在時刻以降でなければなりません。"):
        Deadline(due_date=past_date)
