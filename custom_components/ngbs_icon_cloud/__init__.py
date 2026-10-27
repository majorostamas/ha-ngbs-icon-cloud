"""NGBS iCON integration, via the NGBS cloud."""

from __future__ import annotations

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NgbsCloud
from .const import DOMAIN, MANUFACTURER
from .coordinator import NgbsConfigEntry, NgbsCoordinator

PLATFORMS = [Platform.BINARY_SENSOR, Platform.CLIMATE, Platform.SELECT, Platform.SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: NgbsConfigEntry) -> bool:
    api = NgbsCloud(async_get_clientsession(hass), entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    coordinator = NgbsCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    # Register controllers up front, so room devices can link to them by device ID.
    dev_reg = dr.async_get(hass)
    for serial, c in coordinator.data.items():
        device = dev_reg.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, serial)},
            manufacturer=MANUFACTURER,
            model="iCON controller",
            name=c.get("NAME") or f"iCON {serial}",
            serial_number=serial,
            sw_version=str(c.get("FIRMWARE") or ""),
        )
        coordinator.controller_device_ids[serial] = device.id


    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: NgbsConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
