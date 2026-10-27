"""Polls the NGBS cloud and fans the data out to the entities."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NgbsAuthError, NgbsCloud, NgbsError
from .const import DOMAIN, SCAN_INTERVAL, WRITE_SETTLE_SECONDS

_LOGGER = logging.getLogger(__name__)

type NgbsConfigEntry = ConfigEntry[NgbsCoordinator]


class NgbsCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """data = {serial: controller dict as returned by the cloud}."""

    def __init__(self, hass: HomeAssistant, entry: NgbsConfigEntry, api: NgbsCloud) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.api = api
        self.controller_device_ids: dict[str, str] = {}  # serial -> device registry ID

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            return await self.api.controllers()
        except NgbsAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except (NgbsError, TimeoutError, OSError) as err:
            raise UpdateFailed(str(err)) from err

    def zone(self, serial: str, zone_id: str) -> dict[str, Any] | None:
        for z in (self.data.get(serial) or {}).get("DP") or []:
            if str(z.get("ID")) == zone_id:
                return z
        return None

    async def async_write(
        self, serial: str, attr: str, value: Any, term: str = "", shown_as: str | None = None
    ) -> None:
        """Write, show the new value immediately, then read back the real state.

        shown_as: the field the new value is reported in, if it isn't `attr`.
        """
        try:
            await self.api.write(serial, attr, value, term)
        except NgbsError as err:
            raise UpdateFailed(str(err)) from err
        if term and (z := self.zone(serial, term)) is not None:
            z[shown_as or attr] = value
        elif not term and serial in self.data:
            self.data[serial][shown_as or attr] = value
        self.async_update_listeners()
        await asyncio.sleep(WRITE_SETTLE_SECONDS)
        await self.async_request_refresh()
