"""Tests for the offline watchdog decision (pure function, no HA needed)."""

from custom_components.localtuya.core.offline_watchdog import (
    OFFLINE_GRACE,
    should_force_offline,
)


def _decide(**overrides):
    base = dict(
        connected=False,
        is_sleep=False,
        is_closing=False,
        is_subdevice=False,
        entities_available=True,
        seconds_since_update=OFFLINE_GRACE + 1,
    )
    base.update(overrides)
    return should_force_offline(**base)


def test_stale_entities_on_unreachable_device_are_forced_offline():
    # The 2026-09-03 case: relay cut the bulb's power, connection_lost was lost,
    # entity kept `on` for 15 h.
    assert _decide() is True


def test_within_grace_nothing_happens():
    assert _decide(seconds_since_update=OFFLINE_GRACE - 1) is False
    assert _decide(seconds_since_update=0) is False


def test_exactly_at_grace_fires():
    assert _decide(seconds_since_update=OFFLINE_GRACE) is True


def test_connected_device_is_never_touched():
    assert _decide(connected=True, seconds_since_update=10**6) is False


def test_sleep_device_keeps_last_status():
    assert _decide(is_sleep=True) is False


def test_closing_device_is_left_alone():
    assert _decide(is_closing=True) is False


def test_subdevice_is_driven_by_its_gateway():
    assert _decide(is_subdevice=True) is False


def test_already_unavailable_entities_do_not_refire():
    # After a normal _shutdown_entities the invariant already holds: stay quiet.
    assert _decide(entities_available=False) is False


def test_custom_grace():
    assert _decide(seconds_since_update=20, grace=10) is True
    assert _decide(seconds_since_update=5, grace=10) is False
