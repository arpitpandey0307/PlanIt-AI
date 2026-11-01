"""Tests for timeline generation engine."""
import pytest
from datetime import date, timedelta
from app.engine.timeline import (
    generate_timeline,
    generate_run_of_show,
    generate_tasks,
)
from app.schemas.profile import EventProfile, EventType, VenueType


class TestGenerateTimeline:
    """Tests for the generate_timeline function."""

    def test_wedding_timeline_created(self, wedding_profile):
        """Wedding timeline should be generated with tasks."""
        timeline = generate_timeline(wedding_profile)
        assert timeline is not None
        assert len(timeline.tasks) > 0
        assert timeline.event_id == wedding_profile.id

    def test_birthday_timeline_created(self, birthday_profile):
        """Birthday timeline should be generated with tasks."""
        timeline = generate_timeline(birthday_profile)
        assert timeline is not None
        assert len(timeline.tasks) > 0

    def test_community_timeline_created(self, community_profile):
        """Community timeline should be generated with tasks."""
        timeline = generate_timeline(community_profile)
        assert timeline is not None
        assert len(timeline.tasks) > 0

    def test_timeline_event_date_matches(self, wedding_profile):
        """Timeline event date should match profile."""
        timeline = generate_timeline(wedding_profile)
        assert timeline.event_date == wedding_profile.event_date

    def test_planning_start_before_event(self, wedding_profile):
        """Planning start date should be before event date."""
        timeline = generate_timeline(wedding_profile)
        assert timeline.planning_start_date <= timeline.event_date

    def test_tasks_have_valid_dates(self, wedding_profile):
        """All tasks should have due dates."""
        timeline = generate_timeline(wedding_profile)
        for task in timeline.tasks:
            assert task.due_date is not None
            assert isinstance(task.due_date, date)

    def test_tasks_have_valid_priorities(self, wedding_profile):
        """All tasks should have valid priority levels."""
        timeline = generate_timeline(wedding_profile)
        valid_priorities = {"low", "medium", "high", "urgent"}
        for task in timeline.tasks:
            assert task.priority.value in valid_priorities

    def test_tasks_have_phases(self, wedding_profile):
        """All tasks should be assigned to a phase."""
        timeline = generate_timeline(wedding_profile)
        for task in timeline.tasks:
            assert task.phase is not None
            assert len(task.phase) > 0

    def test_tasks_have_unique_ids(self, wedding_profile):
        """All tasks should have unique IDs."""
        timeline = generate_timeline(wedding_profile)
        ids = [task.id for task in timeline.tasks]
        assert len(ids) == len(set(ids))


class TestShortNotice:
    """Tests for short notice timeline handling."""

    def test_short_notice_detected(self, short_notice_profile):
        """Short notice should be flagged."""
        timeline = generate_timeline(short_notice_profile)
        assert timeline.short_notice is True

    def test_normal_notice_not_flagged(self, wedding_profile):
        """Normal notice should not be flagged."""
        timeline = generate_timeline(wedding_profile)
        assert timeline.short_notice is False

    def test_short_notice_has_tasks(self, short_notice_profile):
        """Short notice timeline should still have tasks."""
        timeline = generate_timeline(short_notice_profile)
        assert len(timeline.tasks) > 0


class TestRunOfShow:
    """Tests for event day schedule generation."""

    def test_wedding_run_of_show(self, wedding_profile):
        """Wedding should have a run of show schedule."""
        slots = generate_run_of_show(wedding_profile)
        assert len(slots) > 0

    def test_birthday_run_of_show(self, birthday_profile):
        """Birthday should have a run of show schedule."""
        slots = generate_run_of_show(birthday_profile)
        assert len(slots) > 0

    def test_community_run_of_show(self, community_profile):
        """Community event should have a run of show schedule."""
        slots = generate_run_of_show(community_profile)
        assert len(slots) > 0

    def test_slots_have_times(self, wedding_profile):
        """All run of show slots should have start and end times."""
        slots = generate_run_of_show(wedding_profile)
        for slot in slots:
            assert slot.start_time is not None
            assert slot.end_time is not None

    def test_slots_have_activities(self, wedding_profile):
        """All slots should have activity descriptions."""
        slots = generate_run_of_show(wedding_profile)
        for slot in slots:
            assert slot.activity is not None
            assert len(slot.activity) > 0

    def test_slots_chronological(self, wedding_profile):
        """Run of show slots should be in chronological order."""
        slots = generate_run_of_show(wedding_profile)
        for i in range(len(slots) - 1):
            assert slots[i].start_time <= slots[i + 1].start_time


class TestOutdoorTasks:
    """Tests for outdoor venue specific tasks."""

    def test_outdoor_wedding_has_tent_task(self, outdoor_wedding_profile):
        """Outdoor wedding should include tent/weather backup task."""
        timeline = generate_timeline(outdoor_wedding_profile)
        task_titles = [t.title.lower() for t in timeline.tasks]
        assert any(
            "tent" in title or "weather" in title or "backup" in title
            for title in task_titles
        )

