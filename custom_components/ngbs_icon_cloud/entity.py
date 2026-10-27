"""Base entities: one device per controller, one per room/thermostat."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import NgbsCoordinator


class NgbsControllerEntity(CoordinatorEntity[NgbsCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: NgbsCoordinator, serial: str, key: str) -> None:
        super().__init__(coordinator)
        self.serial = serial
        self._attr_unique_id = f"{serial}_{key}"
        c = coordinator.data[serial]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer=MANUFACTURER,
            model="iCON controller",
            name=c.get("NAME") or f"iCON {serial}",
            serial_number=serial,
            sw_version=str(c.get("FIRMWARE") or ""),
        )

    @property
    def controller(self) -> dict[str, Any]:
        return self.coordinator.data.get(self.serial) or {}

    @property
    def available(self) -> bool:
        return super().available and bool(self.controller)


class NgbsZoneEntity(NgbsControllerEntity):
    def __init__(self, coordinator: NgbsCoordinator, serial: str, zone_id: str, key: str) -> None:
        super().__init__(coordinator, serial, f"{zone_id}_{key}")
        self.zone_id = zone_id
        z = coordinator.zone(serial, zone_id) or {}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{serial}_{zone_id}")},
            manufacturer=MANUFACTURER,
            model="Thermostat",
            name=z.get("title") or f"Thermostat {zone_id}",
        )
        if via := coordinator.controller_device_ids.get(serial):
            self._attr_device_info["via_device_id"] = via

    @property
    def zone(self) -> dict[str, Any]:
        return self.coordinator.zone(self.serial, self.zone_id) or {}

    @property
    def available(self) -> bool:
        return super().available and bool(self.zone) and self.controller.get("ONLINE", 1) == 1

    async def write(self, attr: str, value: Any) -> None:
        await self.coordinator.async_write(self.serial, attr, value, self.zone_id)


def iter_zones(coordinator: NgbsCoordinator):
    for serial, c in coordinator.data.items():
        for z in c.get("DP") or []:
            yield serial, str(z["ID"])
