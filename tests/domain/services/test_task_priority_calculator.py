# MIT License
# Copyright (c) 2026 Noda Hiroyuki.

"""TaskPriorityCalculatorのテストモジュール."""

import datetime as dt

import pytest

from todo_app.domain.entities.task import Task
from todo_app.domain.services.task_priority_calculator import TaskPriorityCalculator
from todo_app.domain.value_object import Deadline, Priority


@pytest.mark.parametrize(
    ("remaining", "expected"),
    [
        pytest.param(dt.timedelta(microseconds=-1), Priority.HIGH, id="overdue"),
        pytest.param(dt.timedelta(0), Priority.HIGH, id="at-deadline"),
        pytest.param(
            dt.timedelta(microseconds=1), Priority.HIGH, id="just-before-deadline"
        ),
        pytest.param(
            dt.timedelta(hours=12, microseconds=-1),
            Priority.HIGH,
            id="below-twelve-hours",
        ),
        pytest.param(dt.timedelta(hours=12), Priority.HIGH, id="exactly-twelve-hours"),
        pytest.param(
            dt.timedelta(hours=12, microseconds=1),
            Priority.MEDIUM,
            id="over-twelve-hours",
        ),
        pytest.param(dt.timedelta(days=1), Priority.MEDIUM, id="within-two-days"),
        pytest.param(dt.timedelta(days=2), Priority.MEDIUM, id="exactly-two-days"),
        pytest.param(
            dt.timedelta(days=2, microseconds=1),
            Priority.LOW,
            id="over-two-days",
        ),
    ],
)
def test_期限に応じた優先度が返される(
    monkeypatch: pytest.MonkeyPatch,
    remaining: dt.timedelta,
    expected: Priority,
) -> None:
    """期限切れ、12時間以内、2日以内、それ以外の優先度を検証する."""
    real_datetime = dt.datetime
    now = real_datetime(2026, 1, 1, tzinfo=dt.UTC)
    due_date = now + dt.timedelta(days=3)

    class StubDatetime(real_datetime):
        @classmethod
        def now(cls, tz: dt.tzinfo | None = None) -> dt.datetime:
            return now if tz is None else now.astimezone(tz)

    monkeypatch.setattr(dt, "datetime", StubDatetime)
    task = Task(
        title="Test Task",
        description="Test Description",
        due_date=Deadline(due_date),
    )
    now = due_date - remaining

    assert TaskPriorityCalculator.calculate_priority(task) is expected


@pytest.mark.parametrize("priority", list(Priority))
def test_期限がない場合は元の優先度を返す(priority: Priority) -> None:
    """期限がない場合は設定済みの優先度をそのまま返す."""
    task = Task(title="Test Task", description="Test Description", priority=priority)
    assert TaskPriorityCalculator.calculate_priority(task) is priority
