"""Tests for the Bestway climate platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, call

import pytest
from homeassistant.components.climate.const import ATTR_HVAC_MODE, HVACMode
from homeassistant.const import ATTR_TEMPERATURE
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.bestway.climate import AirjetV01HydrojetSpaThermostat
from custom_components.bestway.const import DOMAIN
from custom_components.bestway.bestway.api import BestwayApiResults
from custom_components.bestway.bestway.model import BestwayDeviceStatus, HydrojetHeat

from .common import MockBestwayCoordinator, create_device


@pytest.mark.parametrize(
    ("requested_mode", "expected_heat"),
    ((HVACMode.HEAT, HydrojetHeat.ON), (HVACMode.OFF, HydrojetHeat.OFF)),
)
async def test_hydrojet_set_temperature_translates_hvac_mode(
    hass, requested_mode: HVACMode, expected_heat: HydrojetHeat
) -> None:
    """The Hydrojet thermostat should pass HydrojetHeat enums to the API."""

    device = create_device("device-1", product_name="Hydrojet")
    coordinator = MockBestwayCoordinator(
        hass,
        devices=[device],
        api_overrides={
            "hydrojet_spa_set_heat": AsyncMock(),
            "hydrojet_spa_set_target_temp": AsyncMock(),
        },
        data=BestwayApiResults(devices={device.device_id: BestwayDeviceStatus(0, {})}),
    )

    config_entry = MockConfigEntry(domain=DOMAIN, data={}, entry_id="entry-1")
    thermostat = AirjetV01HydrojetSpaThermostat(coordinator, config_entry, device.device_id)

    await thermostat.async_set_temperature(
        **{ATTR_TEMPERATURE: 30, ATTR_HVAC_MODE: requested_mode}
    )

    assert coordinator.api.hydrojet_spa_set_heat.await_args_list == [
        call(device.device_id, expected_heat)
    ]
    coordinator.api.hydrojet_spa_set_target_temp.assert_awaited_once_with(
        device.device_id, 30
    )
