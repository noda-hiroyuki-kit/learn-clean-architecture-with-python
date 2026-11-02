# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""Value Objectのテストモジュール."""

import datetime as dt

import pytest

from todo_app.domain.entities import value_object
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


def test_deadlineが現在時刻以降なら正常に作成できることを検証する_requires() -> None:
    """期限が現在時刻以降である場合は正常に作成できることを検証する."""
    future_date = dt.datetime.now(tz=dt.UTC) + dt.timedelta(days=1)
    deadline = Deadline(due_date=future_date)
    assert deadline.due_date == future_date


def test_deadlineが現在時刻と同じ場合は正常に作成できることを検証する_requires(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """期限が現在時刻と同じ場合は正常に作成できることを検証する."""
    real_datetime = dt.datetime
    now = real_datetime(2024, 1, 1, 12, 0, 0, tzinfo=dt.UTC)

    class StubDatetime(real_datetime):
        @classmethod
        def now(cls, tz: dt.tzinfo | None = None) -> dt.datetime:
            return now if tz is None else now.astimezone(tz)

    monkeypatch.setattr(value_object.dt, "datetime", StubDatetime)
    deadline = Deadline(due_date=now)
    assert deadline.due_date == now


def _stub_now(monkeypatch: pytest.MonkeyPatch, now: dt.datetime) -> None:
    """value_objectモジュールの現在時刻をnowに固定する."""
    real_datetime = dt.datetime

    class StubDatetime(real_datetime):
        @classmethod
        def now(cls, tz: dt.tzinfo | None = None) -> dt.datetime:
            return now if tz is None else now.astimezone(tz)

    monkeypatch.setattr(value_object.dt, "datetime", StubDatetime)


def test_期限が過ぎている場合はis_overdueがtrueを返すことを検証する_returns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """期限が過ぎている場合はis_overdueがTrueを返すことを検証する."""
    due_date = dt.datetime.now(tz=dt.UTC) + dt.timedelta(hours=1)
    deadline = Deadline(due_date=due_date)
    _stub_now(monkeypatch, due_date + dt.timedelta(seconds=1))
    assert deadline.is_overdue() is True


def test_期限が過ぎていない場合はis_overdueがfalseを返すことを検証する_returns() -> (
    None
):
    """期限が過ぎていない場合はis_overdueがFalseを返すことを検証する."""
    due_date = dt.datetime.now(tz=dt.UTC) + dt.timedelta(days=1)
    deadline = Deadline(due_date=due_date)
    assert deadline.is_overdue() is False


def test_期限が現在時刻と同じ場合はis_overdueがfalseを返すことを検証する_returns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """期限が現在時刻と同じ場合はis_overdueがFalseを返すことを検証する."""
    due_date = dt.datetime.now(tz=dt.UTC) + dt.timedelta(hours=1)
    deadline = Deadline(due_date=due_date)
    _stub_now(monkeypatch, due_date)
    assert deadline.is_overdue() is False
