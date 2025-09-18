"""Tests for Bestway diagnostics."""

from __future__ import annotations

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.bestway.const import (
    CONF_API_ROOT,
    CONF_PASSWORD,
    CONF_USER_TOKEN,
    CONF_USERNAME,
    DOMAIN,
)
from custom_components.bestway.diagnostics import async_get_config_entry_diagnostics
from custom_components.bestway.bestway.api import BestwayApiResults
from custom_components.bestway.bestway.model import BestwayDeviceStatus

from .common import MockBestwayCoordinator, create_device


async def test_diagnostics_mask_sensitive_information(hass) -> None:
    """Diagnostics should redact sensitive config data and mask identifiers."""

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_USERNAME: "user@example.com",
            CONF_PASSWORD: "secret",
            CONF_USER_TOKEN: "token",
            CONF_API_ROOT: "https://api.example.com",
        },
        entry_id="entry-1",
        title="Bestway",
    )

    device = create_device("device-1", product_name="Hydrojet", alias="Spa")
    status = BestwayDeviceStatus(1234567890, {"temp": 37})
    coordinator = MockBestwayCoordinator(
        hass,
        devices=[device],
        data=BestwayApiResults(devices={device.device_id: status}),
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    diagnostics = await async_get_config_entry_diagnostics(hass, entry)

    redacted_data = diagnostics["config_entry"]["data"]
    assert redacted_data[CONF_USERNAME] != "user@example.com"
    assert redacted_data[CONF_PASSWORD] != "secret"
    assert redacted_data[CONF_USER_TOKEN] != "token"

    sanitized_device = diagnostics["devices"][0]
    assert sanitized_device["did"] != device.device_id
    assert sanitized_device["dev_alias"] == "Spa"

    status_keys = list(diagnostics["status"].keys())
    assert status_keys
    assert device.device_id not in status_keys
    assert diagnostics["status"][status_keys[0]]["attrs"] == status.attrs
