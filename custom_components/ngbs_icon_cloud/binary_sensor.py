"""Controller connectivity and per-room valve state."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import NgbsConfigEntry
from .entity import NgbsControllerEntity, NgbsZoneEntity, iter_zones


async def async_setup_entry(
    hass: HomeAssistant, entry: NgbsConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    entities: list[BinarySensorEntity] = [NgbsOnline(coordinator, serial) for serial in coordinator.data]
    entities += [NgbsValve(coordinator, serial, zid) for serial, zid in iter_zones(coordinator)]
    async_add_entities(entities)


class NgbsOnline(NgbsControllerEntity, BinarySensorEntity):
    _attr_name = "Online"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, serial: str) -> None:
        super().__init__(coordinator, serial, "online")

    @property
    def is_on(self) -> bool:
        return self.controller.get("ONLINE") == 1


class NgbsValve(NgbsZoneEntity, BinarySensorEntity):
    _attr_name = "Valve"
    _attr_device_class = BinarySensorDeviceClass.OPENING
    _attr_icon = "mdi:valve"

    def __init__(self, coordinator, serial: str, zone_id: str) -> None:
        super().__init__(coordinator, serial, zone_id, "valve")

    @property
    def is_on(self) -> bool:
        return self.zone.get("OUT") == 1
