"""Temperature/humidity sensors, usable in history graphs and automations."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import NgbsConfigEntry
from .entity import NgbsControllerEntity, NgbsZoneEntity, iter_zones


@dataclass(frozen=True, kw_only=True)
class NgbsSensorDescription(SensorEntityDescription):
    value: Callable[[dict[str, Any]], Any]


def _temp(key: str, name: str, field: str) -> NgbsSensorDescription:
    return NgbsSensorDescription(
        key=key,
        name=name,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value=lambda d: d.get(field),
    )


ZONE_SENSORS = (
    _temp("temperature", "Temperature", "TEMP"),
    NgbsSensorDescription(
        key="humidity",
        name="Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        value=lambda d: d.get("RH"),
    ),
    _temp("dew_point", "Dew point", "DEW"),
    _temp("target", "Target temperature", "REQ"),
)

CONTROLLER_SENSORS = (
    _temp("water_temperature", "Water temperature", "WTEMP"),
    _temp("outside_temperature", "Outside temperature", "ETEMP"),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: NgbsConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    entities: list[SensorEntity] = [
        NgbsZoneSensor(coordinator, serial, zid, d) for serial, zid in iter_zones(coordinator) for d in ZONE_SENSORS
    ]
    entities += [
        NgbsControllerSensor(coordinator, serial, d)
        for serial, c in coordinator.data.items()
        for d in CONTROLLER_SENSORS
        if d.value(c) is not None  # sensor not installed
    ]
    async_add_entities(entities)


class NgbsZoneSensor(NgbsZoneEntity, SensorEntity):
    entity_description: NgbsSensorDescription

    def __init__(self, coordinator, serial: str, zone_id: str, description: NgbsSensorDescription) -> None:
        super().__init__(coordinator, serial, zone_id, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        return self.entity_description.value(self.zone)


class NgbsControllerSensor(NgbsControllerEntity, SensorEntity):
    entity_description: NgbsSensorDescription

    def __init__(self, coordinator, serial: str, description: NgbsSensorDescription) -> None:
        super().__init__(coordinator, serial, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        return self.entity_description.value(self.controller)
