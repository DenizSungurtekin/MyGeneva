from __future__ import annotations

from datetime import datetime, timezone

from pipeline.dedup import compute_dedup_key


def _dt(hour_utc: int = 22) -> datetime:
    return datetime(2026, 9, 26, hour_utc, 0, tzinfo=timezone.utc)


def test_same_title_date_venue_same_key():
    """Same real-world event across sources → same key."""
    k1 = compute_dedup_key("Nuit Techno", _dt(), venue_name="Motel Campo")
    k2 = compute_dedup_key("Nuit Techno", _dt(), venue_name="Motel Campo")
    assert k1 == k2


def test_place_id_overrides_venue_name():
    """When a place_id is present, we use it and ignore the venue string."""
    k_pid = compute_dedup_key("A", _dt(), place_id=42, venue_name="Whatever")
    k_pid_other = compute_dedup_key("A", _dt(), place_id=42, venue_name="Different")
    assert k_pid == k_pid_other

    # place_id different → different key
    k_pid2 = compute_dedup_key("A", _dt(), place_id=43, venue_name="Whatever")
    assert k_pid != k_pid2


def test_accents_and_case_normalized():
    k1 = compute_dedup_key("Les Pâquis Sont à la Rue", _dt(), venue_name="Genève")
    k2 = compute_dedup_key("les paquis sont a la rue", _dt(), venue_name="GENEVE")
    assert k1 == k2


def test_different_days_different_keys():
    k1 = compute_dedup_key("Same title", _dt(), venue_name="Same venue")
    later = datetime(2026, 9, 27, 22, 0, tzinfo=timezone.utc)
    k2 = compute_dedup_key("Same title", later, venue_name="Same venue")
    assert k1 != k2


def test_local_date_boundary_crosses_midnight_utc():
    """22h UTC on Fri = 00h Zurich Sat. Two events at 22h and 23h UTC same
    calendar day in UTC map to the SAME local date (Sat) → same key."""
    a = compute_dedup_key("X", datetime(2026, 9, 25, 22, 0, tzinfo=timezone.utc), venue_name="V")
    b = compute_dedup_key("X", datetime(2026, 9, 25, 23, 0, tzinfo=timezone.utc), venue_name="V")
    assert a == b


def test_place_id_none_falls_back_to_venue():
    """No place_id → hash uses normalized venue name."""
    k1 = compute_dedup_key("T", _dt(), venue_name="Motel Campo")
    k2 = compute_dedup_key("T", _dt(), venue_name="motel  campo")     # extra whitespace
    assert k1 == k2
