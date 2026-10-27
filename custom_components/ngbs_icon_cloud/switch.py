"""Per-room switches: ECO mode and parental lock."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import NgbsConfigEntry
from .entity import NgbsZoneEntity, iter_zones

# key, name, attribute, icon, category
SWITCHES = (
    ("eco", "ECO mode", "CE", "mdi:leaf", None),
    ("parental_lock", "Parental lock", "PL", "mdi:lock", EntityCategory.CONFIG),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: NgbsConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        NgbsZoneSwitch(coordinator, serial, zid, *spec) for serial, zid in iter_zones(coordinator) for spec in SWITCHES
    )


class NgbsZoneSwitch(NgbsZoneEntity, SwitchEntity):
    def __init__(self, coordinator, serial, zone_id, key, name, attr, icon, category) -> None:
        super().__init__(coordinator, serial, zone_id, key)
        self._attr_name = name
        self._attr_icon = icon
        self._attr_entity_category = category
        self._ngbs_attr = attr

    @property
    def is_on(self) -> bool:
        return bool(self.zone.get(self._ngbs_attr))

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.write(self._ngbs_attr, 1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.write(self._ngbs_attr, 0)
