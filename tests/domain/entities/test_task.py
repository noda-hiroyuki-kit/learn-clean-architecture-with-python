# MIT License
# Copyright (c) 2026 Noda Hiroyuki.
"""Taskエンティティのテスト."""

import datetime as dt

import pytest

from todo_app.domain.entities.task import (
    COMPLETION_NOTES_MAX_LENGTH,
    DESCRIPTION_MAX_LENGTH,
    TITLE_MAX_LENGTH,
    Task,
)
from todo_app.domain.value_object import Deadline, Priority, TaskStatus


class TestTask:
    """Taskエンティティのテスト."""

    class TestTaskが正しく生成される:
        """Taskが正しく生成される."""

        @pytest.fixture(scope="class")
        @classmethod
        def fixture_task(cls) -> Task:
            """テスト用のTaskを生成するフィクスチャ."""
            return Task(
                title="Test Task",
                description="Test Description",
            )

        def test_タイトルが設定される(self, fixture_task: Task) -> None:
            """タイトルが設定されることを確認する."""
            assert fixture_task.title == "Test Task"

        def test_idが自動生成される(self, fixture_task: Task) -> None:
            """idが自動生成されることを確認する."""
            assert fixture_task.id is not None

        def test_descriptionが設定される(self, fixture_task: Task) -> None:
            """descriptionが設定されることを確認する."""
            assert fixture_task.description == "Test Description"

        def test_project_idは既定でNoneに設定される(self, fixture_task: Task) -> None:
            """project_idが既定でNoneに設定されることを確認する."""
            assert fixture_task.project_id is None

        def test_priorityは既定でMEDIUMに設定される(self, fixture_task: Task) -> None:
            """priorityが既定でMEDIUMに設定されることを確認する."""
            assert fixture_task.priority == Priority.MEDIUM

        def test_statusは既定でTODOに設定される(self, fixture_task: Task) -> None:
            """statusが既定でTODOに設定されることを確認する."""
            assert fixture_task.status == TaskStatus.TODO

        def test_completed_atは既定でNoneに設定される(self, fixture_task: Task) -> None:
            """completed_atが既定でNoneに設定されることを確認する."""
            assert fixture_task.completed_at is None

        def test_completion_notesは既定でNoneに設定される(
            self, fixture_task: Task
        ) -> None:
            """completion_notesが既定でNoneに設定されることを確認する."""
            assert fixture_task.completion_notes is None

        def test最大長ちょうどのtitleで生成できる(self) -> None:
            """最大長ちょうどのtitleでTaskを生成できることを確認する."""
            title = "a" * TITLE_MAX_LENGTH
            task = Task(title=title, description="")
            assert task.title == title

        def test最大長ちょうどのdescriptionで生成できる(self) -> None:
            """最大長ちょうどのdescriptionでTaskを生成できることを確認する."""
            description = "a" * DESCRIPTION_MAX_LENGTH
            task = Task(title="タスク", description=description)
            assert task.description == description

    class Test検証エラーになる:
        """不正なtitleやdescriptionは生成時に拒否される."""

        @pytest.mark.parametrize("title", ["", "   ", "\t\n", "\u3000"])
        def test空のtitleはvalue_errorになる(self, title: str) -> None:
            """空文字または空白のみのtitleはValueErrorになることを確認する."""
            with pytest.raises(ValueError, match=r"^タイトルが必要です$"):
                Task(title=title, description="")

        def test_titleが最大長を超えるとvalue_errorになる(self) -> None:
            """titleが最大長を超える場合はValueErrorになることを確認する."""
            with pytest.raises(
                ValueError,
                match=f"タイトルは{TITLE_MAX_LENGTH}文字以内である必要があります",
            ):
                Task(title="a" * (TITLE_MAX_LENGTH + 1), description="")

        def test_descriptionが最大長を超えるとvalue_errorになる(self) -> None:
            """descriptionが最大長を超える場合はValueErrorになることを確認する."""
            with pytest.raises(
                ValueError,
                match=f"説明は{DESCRIPTION_MAX_LENGTH}文字以内である必要があります",
            ):
                Task(title="タスク", description="a" * (DESCRIPTION_MAX_LENGTH + 1))

    class TestTaskのメソッドのテスト:
        """Taskのメソッドに関するテスト."""

        @pytest.fixture
        @classmethod
        def fixture_task(cls) -> Task:
            """テスト用のTaskを生成するフィクスチャ."""
            return Task(
                title="Complete project proposal",
                description="Draft and review the proposal for the new client project",
                due_date=Deadline(dt.datetime.now(tz=dt.UTC) + dt.timedelta(days=7)),
                priority=Priority.HIGH,
            )

        @pytest.fixture
        @classmethod
        def fixture_task_overdue(cls) -> Task:
            """テスト用のTaskを生成するフィクスチャ."""
            return Task(
                title="Complete project proposal",
                description="Draft and review the proposal for the new client project",
                due_date=Deadline(dt.datetime.now(tz=dt.UTC) + dt.timedelta(days=1)),
                priority=Priority.HIGH,
            )

        @pytest.fixture
        @classmethod
        def fixture_task_due_none(cls) -> Task:
            """期限が設定されていないTaskを生成するフィクスチャ."""
            return Task(
                title="Complete project proposal",
                description="Draft and review the proposal for the new client project",
                due_date=None,
                priority=Priority.HIGH,
            )

        def test_statusがtodoの時はstartできる(self, fixture_task: Task) -> None:
            """statusがTODOの時はstartできることを確認する."""
            fixture_task.start()
            assert fixture_task.status == TaskStatus.IN_PROGRESS

        def test_statusがin_progressの時はstartできない(
            self, fixture_task: Task
        ) -> None:
            """statusがIN_PROGRESSの時はstartできないことを確認する."""
            fixture_task.start()
            with pytest.raises(
                ValueError, match="TaskのstatusがTODOの場合のみ開始できます。"
            ):
                fixture_task.start()

        def test_statusがtodoの時はcompletedにできる(self, fixture_task: Task) -> None:
            """statusがTODOの時はcompletedにできることを確認する."""
            fixture_task.complete()
            assert fixture_task.status == TaskStatus.DONE

        def test_statusがin_progressの時はcompletedにできる(
            self, fixture_task: Task
        ) -> None:
            """statusがIN_PROGRESSの時はcompletedにできることを確認する."""
            fixture_task.start()
            fixture_task.complete()
            assert fixture_task.status == TaskStatus.DONE

        def test_statusがdoneの時はcompletedにできない(
            self, fixture_task: Task
        ) -> None:
            """statusがDONEの時はcompletedにできないことを確認する."""
            fixture_task.complete()
            with pytest.raises(ValueError, match="Taskは既に完了しています。"):
                fixture_task.complete()

        class TestCompleteするとCompletedAtに完了時刻が記録される:
            """completeするとcompleted_atにUTCの完了時刻が記録される."""

            @pytest.fixture
            @classmethod
            def fixture_completion(
                cls, fixture_task: Task
            ) -> tuple[dt.datetime, dt.datetime, dt.datetime]:
                """completeを実行し、実行前の時刻・完了時刻・実行後の時刻を返すフィクスチャ."""
                before = dt.datetime.now(tz=dt.UTC)
                fixture_task.complete()
                after = dt.datetime.now(tz=dt.UTC)
                completed_at = fixture_task.completed_at
                assert completed_at is not None
                return (before, completed_at, after)

            def test_completed_atがutcで記録される(
                self, fixture_completion: tuple[dt.datetime, dt.datetime, dt.datetime]
            ) -> None:
                """completed_atがUTCで記録されることを確認する."""
                assert fixture_completion[1].tzinfo == dt.UTC

            def test_completed_atが実行前後の時刻の範囲内になる(
                self, fixture_completion: tuple[dt.datetime, dt.datetime, dt.datetime]
            ) -> None:
                """completed_atがcomplete実行前後の時刻の範囲内になることを確認する."""
                before, completed_at, after = fixture_completion
                assert before <= completed_at <= after

        def test_notesを指定してcompleteするとcompletion_notesが設定される(
            self, fixture_task: Task
        ) -> None:
            """notesを指定してcompleteするとcompletion_notesが設定されることを確認する."""
            fixture_task.complete(notes="完了メモ")
            assert fixture_task.completion_notes == "完了メモ"

        def test_notesを指定せずにcompleteするとcompletion_notesはNoneのまま(
            self, fixture_task: Task
        ) -> None:
            """notesを指定せずにcompleteするとcompletion_notesがNoneのままであることを確認する."""
            fixture_task.complete()
            assert fixture_task.completion_notes is None

        def test最大長のnotesを指定してcompleteできる(self, fixture_task: Task) -> None:
            """最大長ちょうどのnotesでTaskを完了できることを確認する."""
            notes = "a" * COMPLETION_NOTES_MAX_LENGTH
            fixture_task.complete(notes=notes)
            assert fixture_task.completion_notes == notes

        def test最大長を超えるnotesを指定するとvalue_errorになる(
            self, fixture_task: Task
        ) -> None:
            """最大長を超えるnotesはValueErrorになることを確認する."""
            notes = "a" * (COMPLETION_NOTES_MAX_LENGTH + 1)
            with pytest.raises(
                ValueError,
                match=f"完了ノートは{COMPLETION_NOTES_MAX_LENGTH}文字以内である必要があります",
            ):
                fixture_task.complete(notes=notes)

        def test_期限を過ぎていないときはis_overdueはFalseになる(
            self, fixture_task: Task
        ) -> None:
            """期限を過ぎていないときはis_overdueがFalseになることを確認する."""
            assert fixture_task.is_overdue() is False

        @pytest.fixture
        @classmethod
        def fixture_overdue_due_date(cls, fixture_task_overdue: Task) -> dt.datetime:
            """期限切れ判定用のTaskの期限日時を返すフィクスチャ."""
            due_date = fixture_task_overdue.due_date
            assert due_date is not None
            return due_date.due_date

        def test_期限を過ぎているときはis_overdueはTrueになる(
            self,
            fixture_task_overdue: Task,
            fixture_overdue_due_date: dt.datetime,
            monkeypatch: pytest.MonkeyPatch,
        ) -> None:
            """期限を過ぎているときはis_overdueがTrueになることを確認する."""
            real_datetime = dt.datetime
            now = fixture_overdue_due_date + dt.timedelta(seconds=1)

            class StubDatetime(real_datetime):
                @classmethod
                def now(cls, tz: dt.tzinfo | None = None) -> dt.datetime:
                    return now if tz is None else now.astimezone(tz)

            monkeypatch.setattr(dt, "datetime", StubDatetime)
            assert fixture_task_overdue.is_overdue() is True

        def test_期限が設定されていないときはis_overdueはFalseになる(
            self, fixture_task_due_none: Task
        ) -> None:
            """期限が設定されていないときはis_overdueがFalseになることを確認する."""
            assert fixture_task_due_none.is_overdue() is False
