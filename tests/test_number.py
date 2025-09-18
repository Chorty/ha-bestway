"""Tests for the Bestway number platform."""

from __future__ import annotations

from unittest.mock import AsyncMock

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.bestway.const import DOMAIN
from custom_components.bestway.bestway.api import BestwayApiResults
from custom_components.bestway.bestway.model import BestwayDeviceStatus
from custom_components.bestway.number import PoolFilterTimeNumber, _POOL_FILTER_TIME

from .common import MockBestwayCoordinator, create_device


async def test_pool_filter_time_requests_refresh(hass) -> None:
    """Setting the filter time should request a refresh."""

    device = create_device("device-1", product_name="泳池过滤器")
    coordinator = MockBestwayCoordinator(
        hass,
        devices=[device],
        api_overrides={"pool_filter_set_time": AsyncMock()},
        data=BestwayApiResults(
            devices={device.device_id: BestwayDeviceStatus(0, {"time": 0})}
        ),
    )

    config_entry = MockConfigEntry(domain=DOMAIN, data={}, entry_id="entry-1")
    number = PoolFilterTimeNumber(
        coordinator,
        config_entry,
        device.device_id,
        _POOL_FILTER_TIME,
    )

    await number.async_set_native_value(4)

    coordinator.api.pool_filter_set_time.assert_awaited_once_with(device.device_id, 4)
    coordinator.async_refresh.assert_awaited_once()
