"""Constants for the NGBS iCON cloud integration."""

from datetime import timedelta

DOMAIN = "ngbs_icon_cloud"
MANUFACTURER = "NGBS"

API_URL = "https://stat.ngbsh.hu"
APP_VERSION = "1.2.10"  # version of the mobile app this mimics

SCAN_INTERVAL = timedelta(seconds=30)
# The cloud relays writes to the controller; wait this long before reading back.
WRITE_SETTLE_SECONDS = 3
