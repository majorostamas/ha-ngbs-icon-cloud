"""Async client for the NGBS iCON cloud API (the one the mobile app uses)."""

from __future__ import annotations

import time
from typing import Any

import aiohttp

from .const import API_URL, APP_VERSION


class NgbsError(Exception):
    """Generic API error."""


class NgbsAuthError(NgbsError):
    """Wrong email or password."""


class NgbsCloud:
    def __init__(self, session: aiohttp.ClientSession, username: str, password: str) -> None:
        self._session = session
        self._username = username
        self._password = password
        self._token: str | None = None

    async def login(self) -> None:
        async with self._session.post(
            f"{API_URL}/api/auth",
            json={"username": self._username, "password": self._password, "version": APP_VERSION},
            timeout=aiohttp.ClientTimeout(total=20),
        ) as r:
            if r.status in (400, 401, 403):
                raise NgbsAuthError("Wrong email or password")
            if r.status != 200:
                raise NgbsError(f"Login failed: HTTP {r.status}")
            data = await r.json(content_type=None)
        if not data.get("token"):
            raise NgbsError("Login response has no token")
        self._token = data["token"]

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        if not self._token:
            await self.login()
        for attempt in (1, 2):
            async with self._session.request(
                method,
                f"{API_URL}{path}",
                headers={"Authorization": f"Bearer {self._token}"},
                timeout=aiohttp.ClientTimeout(total=20),
                **kwargs,
            ) as r:
                # An expired token gets 401, or 403 "User not found"
                if r.status in (401, 403) and attempt == 1:
                    await self.login()
                    continue
                if r.status != 200:
                    raise NgbsError(f"{method} {path} failed: HTTP {r.status}")
                return await r.json(content_type=None)
        raise NgbsError(f"{method} {path} failed after re-login")

    async def controllers(self) -> dict[str, dict[str, Any]]:
        """All controllers on the account, keyed by serial number."""
        data = await self._request(
            "GET", "/api/icon/iconlist", params={"hideLogs": "true", "_t": str(int(time.time() * 1000))}
        )
        icons = data.get("ICONS") or {}
        icons = icons.values() if isinstance(icons, dict) else icons
        return {str(c["SNR"]): c for c in icons}

    async def write(self, serial: str, attr: str, value: Any, term: str = "") -> None:
        """Write a value. term is the thermostat ID, or "" for the controller."""
        data = await self._request(
            "POST", "/api/icon/set", json={"SNR": serial, "TERM": term, "attr": attr, "value": value}
        )
        write = (data or {}).get("WRITE") or {}
        if write.get("status") not in (1, None):
            raise NgbsError(f"Controller rejected {attr}={value}: {write}")
