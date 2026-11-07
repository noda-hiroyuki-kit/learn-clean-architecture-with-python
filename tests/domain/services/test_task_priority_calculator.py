# MIT License
# Copyright (c) 2026 Noda Hiroyuki.

"""TaskPriorityCalculatorのテストモジュール."""

import datetime as dt
from typing import Self

import pytest

from todo_app.domain.entities.task import Task
from todo_app.domain.services.task_priority_calculator import TaskPriorityCalculator
from todo_app.domain.value_object import Deadline, Priority


@pytest.mark.parametrize(
    ("remaining", "expected"),
    [
        pytest.param(dt.timedelta(microseconds=-1), Priority.HIGH, id="overdue"),
        pytest.param(dt.timedelta(0), Priority.MEDIUM, id="at-deadline"),
        pytest.param(
            dt.timedelta(microseconds=1), Priority.MEDIUM, id="just-before-deadline"
        ),
        pytest.param(dt.timedelta(days=1), Priority.MEDIUM, id="within-two-days"),
        pytest.param(dt.timedelta(days=2), Priority.MEDIUM, id="exactly-two-days"),
        pytest.param(
            dt.timedelta(days=2, microseconds=1),
            Priority.LOW,
            id="over-two-days",
        ),
        pytest.param(None, Priority.LOW, id="no-deadline"),
    ],
)
def test_期限に応じた優先度が返される(
    monkeypatch: pytest.MonkeyPatch,
    remaining: dt.timedelta | None,
    expected: Priority,
) -> None:
    """期限切れ・期限まで2日以内・それ以外の優先度を検証する."""
    real_datetime = dt.datetime
    now = real_datetime(2026, 1, 1, tzinfo=dt.UTC)
    due_date = now + dt.timedelta(days=3)

    class StubDatetime(real_datetime):
        @classmethod
        def now(cls, tz: dt.tzinfo | None = None) -> Self:
            return cls.fromtimestamp(now.timestamp(), tz)

    monkeypatch.setattr(dt, "datetime", StubDatetime)
    task = Task(
        title="Test Task",
        description="Test Description",
        due_date=Deadline(due_date) if remaining is not None else None,
    )
    if remaining is not None:
        now = due_date - remaining

    assert TaskPriorityCalculator.calculate_priority(task) is expected
