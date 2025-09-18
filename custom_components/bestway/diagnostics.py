"""Diagnostics support for the Bestway integration."""

from __future__ import annotations

from collections.abc import Mapping

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .bestway.api import BestwayApi
from .const import CONF_PASSWORD, CONF_USER_TOKEN, CONF_USERNAME, DOMAIN

TO_REDACT = {CONF_PASSWORD, CONF_USER_TOKEN, CONF_USERNAME}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> Mapping[str, object]:
    """Return diagnostics for a config entry."""

    coordinator = hass.data[DOMAIN][entry.entry_id]

    sanitized_devices = BestwayApi._sanitize_bindings_response(  # pylint: disable=protected-access
        {
            "devices": [
                {
                    "did": device.device_id,
                    "product_name": device.product_name,
                    "dev_alias": device.alias,
                    "mcu_soft_version": device.mcu_soft_version,
                    "mcu_hard_version": device.mcu_hard_version,
                    "wifi_soft_version": device.wifi_soft_version,
                    "wifi_hard_version": device.wifi_hard_version,
                    "is_online": device.is_online,
                }
                for device in coordinator.api.devices.values()
            ]
        }
    )["devices"]

    status_snapshot: dict[str, object] = {}
    devices_state = getattr(coordinator.data, "devices", {})
    for device_id, status in devices_state.items():
        status_snapshot["*" * len(device_id)] = {
            "timestamp": status.timestamp,
            "attrs": status.attrs,
        }

    return {
        "config_entry": {
            "entry_id": entry.entry_id,
            "title": entry.title,
            "data": async_redact_data(entry.data, TO_REDACT),
        },
        "devices": sanitized_devices,
        "status": status_snapshot,
    }

