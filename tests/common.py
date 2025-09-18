"""Test helpers for the Bestway integration."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Iterable
from unittest.mock import AsyncMock

from custom_components.bestway.bestway.model import BestwayDevice


def create_device(
    device_id: str,
    *,
    product_name: str = "Hydrojet",
    alias: str = "Bestway Spa",
    protocol_version: int = 1,
    mcu_soft_version: str = "1.0",
    mcu_hard_version: str = "1.0",
    wifi_soft_version: str = "1.0",
    wifi_hard_version: str = "1.0",
    is_online: bool = True,
) -> BestwayDevice:
    """Create a BestwayDevice instance for testing."""

    return BestwayDevice(
        protocol_version,
        device_id,
        product_name,
        alias,
        mcu_soft_version,
        mcu_hard_version,
        wifi_soft_version,
        wifi_hard_version,
        is_online,
    )


class MockBestwayCoordinator:
    """Minimal coordinator implementation for entity tests."""

    def __init__(
        self,
        hass,
        *,
        devices: Iterable[BestwayDevice] | None = None,
        api_overrides: dict[str, object] | None = None,
        data: object | None = None,
        data_devices: dict[str, object] | None = None,
    ) -> None:
        self.hass = hass
        self.last_update_success = True
        self._listeners: list[object] = []
        self.api = SimpleNamespace()
        self.api.devices = {}
        if devices:
            self.api.devices.update({device.device_id: device for device in devices})
        if api_overrides:
            for name, value in api_overrides.items():
                setattr(self.api, name, value)
        self.async_refresh = AsyncMock()
        if data is not None:
            self.data = data
        else:
            self.data = SimpleNamespace(devices=data_devices or {})

    def async_add_listener(self, update_callback):
        """Pretend to register a coordinator listener."""

        self._listeners.append(update_callback)

        def _remove_listener():
            if update_callback in self._listeners:
                self._listeners.remove(update_callback)

        return _remove_listener

