"""Controller-wide heating/cooling selector, like the toggle in the app."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import NgbsConfigEntry
from .entity import NgbsControllerEntity

HEATING = "heating"
COOLING = "cooling"


async def async_setup_entry(
    hass: HomeAssistant, entry: NgbsConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    # The app only offers the toggle when the controller allows switching.
    async_add_entities(
        NgbsHeatCoolSelect(coordinator, serial) for serial, c in coordinator.data.items() if c.get("HC_SWITCH")
    )


class NgbsHeatCoolSelect(NgbsControllerEntity, SelectEntity):
    _attr_name = "Heating/cooling"
    _attr_options = [HEATING, COOLING]

    def __init__(self, coordinator, serial: str) -> None:
        super().__init__(coordinator, serial, "heat_cool")

    @property
    def icon(self) -> str:
        return "mdi:snowflake" if self.controller.get("HCMASTER") else "mdi:fire"

    @property
    def current_option(self) -> str:
        return COOLING if self.controller.get("HCMASTER") else HEATING

    async def async_select_option(self, option: str) -> None:
        # Pump and valves pause for a few minutes after a changeover.
        await self.coordinator.async_write(self.serial, "HC", int(option == COOLING), shown_as="HCMASTER")
