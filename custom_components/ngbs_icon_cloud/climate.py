"""A thermostat card per room."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    PRESET_COMFORT,
    PRESET_ECO,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import NgbsConfigEntry
from .entity import NgbsZoneEntity, iter_zones


async def async_setup_entry(
    hass: HomeAssistant, entry: NgbsConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(NgbsClimate(coordinator, serial, zid) for serial, zid in iter_zones(coordinator))


class NgbsClimate(NgbsZoneEntity, ClimateEntity):
    _attr_name = None  # the entity takes the room's name
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 0.5
    _attr_preset_modes = [PRESET_COMFORT, PRESET_ECO]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE

    def __init__(self, coordinator, serial: str, zone_id: str) -> None:
        super().__init__(coordinator, serial, zone_id, "climate")

    @property
    def hvac_mode(self) -> HVACMode:
        return HVACMode.COOL if self.zone.get("HC") else HVACMode.HEAT

    @property
    def hvac_modes(self) -> list[HVACMode]:
        # Heating/cooling is decided by the controller (master thermostat), so only
        # the current mode is offered.
        return [self.hvac_mode]

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        pass

    @property
    def hvac_action(self) -> HVACAction:
        if not self.zone.get("OUT"):
            return HVACAction.IDLE
        return HVACAction.COOLING if self.zone.get("HC") else HVACAction.HEATING

    @property
    def current_temperature(self) -> float | None:
        return self.zone.get("TEMP")

    @property
    def current_humidity(self) -> float | None:
        return self.zone.get("RH")

    @property
    def target_temperature(self) -> float | None:
        return self.zone.get("REQ")

    @property
    def min_temp(self) -> float:
        return self.zone.get("TMIN") or 5

    @property
    def max_temp(self) -> float:
        return self.zone.get("TMAX") or 35

    @property
    def preset_mode(self) -> str:
        return PRESET_ECO if self.zone.get("CE") else PRESET_COMFORT

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            await self.write("REQ", temperature)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        await self.write("CE", int(preset_mode == PRESET_ECO))
