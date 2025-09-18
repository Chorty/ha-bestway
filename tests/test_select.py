"""Tests for the Bestway select platform."""

from __future__ import annotations

from unittest.mock import AsyncMock

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.bestway.const import DOMAIN
from custom_components.bestway.bestway.api import BestwayApiResults
from custom_components.bestway.bestway.model import BestwayDeviceStatus, BubblesLevel
from custom_components.bestway.select import (
    ThreeWaySpaBubblesSelect,
    _AIRJET_V01_BUBBLES_SELECT_DESCRIPTION,
)

from .common import MockBestwayCoordinator, create_device


async def test_bubbles_select_requests_refresh(hass) -> None:
    """Selecting a bubbles option should trigger a refresh."""

    device = create_device("device-1", product_name="Airjet_V01")
    coordinator = MockBestwayCoordinator(
        hass,
        devices=[device],
        api_overrides={"airjet_v01_spa_set_bubbles": AsyncMock()},
        data=BestwayApiResults(
            devices={device.device_id: BestwayDeviceStatus(0, {"wave": 0})}
        ),
    )

    config_entry = MockConfigEntry(domain=DOMAIN, data={}, entry_id="entry-1")
    select = ThreeWaySpaBubblesSelect(
        coordinator,
        config_entry,
        device.device_id,
        _AIRJET_V01_BUBBLES_SELECT_DESCRIPTION,
    )

    await select.async_select_option("MEDIUM")

    coordinator.api.airjet_v01_spa_set_bubbles.assert_awaited_once_with(
        device.device_id, BubblesLevel.MEDIUM
    )
    coordinator.async_refresh.assert_awaited_once()
