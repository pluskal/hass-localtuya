"""Decision logic for the device offline watchdog (pure, no Home Assistant imports).

A LocalTuya entity is `available` while it holds a status or its device is connected.
The status is only cleared by TuyaDevice._shutdown_entities(), which disconnected()
schedules; every code path that loses that schedule leaves the entities available with
a stale status for as long as the device stays unreachable. The watchdog in
coordinator.TuyaDevice enforces the invariant periodically; this module holds the
decision so it can be unit-tested without Home Assistant.
"""

from __future__ import annotations

# Seconds since the last status update after which a disconnected device must not keep
# its entities available. Comfortably above the normal detection path (two missed
# heartbeats + TIMEOUT_CONNECT, roughly 30 s) so a healthy reconnect is never disturbed.
OFFLINE_GRACE = 60

# How often the watchdog evaluates the invariant.
OFFLINE_WATCHDOG_INTERVAL_SECONDS = 30


def should_force_offline(
    *,
    connected: bool,
    is_sleep: bool,
    is_closing: bool,
    is_subdevice: bool,
    entities_available: bool,
    seconds_since_update: float,
    grace: float = OFFLINE_GRACE,
) -> bool:
    """Return True when the device's entities must be forced unavailable.

    connected:           the device has a live pytuya connection
    is_sleep:            low-power device that legitimately keeps its last status
    is_closing:          the device is being unloaded
    is_subdevice:        gateway child; its availability is driven by the gateway
    entities_available:  at least one entity still reports itself available
    seconds_since_update: time since the device last delivered a status
    """
    if is_closing or is_sleep or is_subdevice or connected:
        return False
    if not entities_available:
        return False
    return seconds_since_update >= grace
