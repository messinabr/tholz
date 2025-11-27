import logging
from datetime import datetime
import zoneinfo 

from homeassistant.components.select import SelectEntity
from homeassistant.util import dt as dt_util
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Lista de Fusos (Mantive a mesma lista completa)
TIMEZONES = [
    "America/Sao_Paulo", "America/Manaus", "America/Rio_Branco", "America/Belem",
    "America/Fortaleza", "America/Recife", "America/Salvador", "America/Cuiaba",
    "America/Campo_Grande", "America/Bahia", "America/Noronha",
    "America/Argentina/Buenos_Aires", "America/Santiago", "America/Montevideo",
    "America/Bogota", "America/Lima", "America/Caracas",
    "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
    "America/Toronto", "America/Vancouver", "America/Mexico_City",
    "Europe/Lisbon", "Europe/London", "Europe/Paris", "Europe/Madrid",
    "Europe/Berlin", "Europe/Rome", "Europe/Amsterdam", "Europe/Zurich",
    "Europe/Athens", "Europe/Moscow", "Europe/Istanbul",
    "Asia/Dubai", "Asia/Jerusalem", "Asia/Kolkata", "Asia/Bangkok",
    "Asia/Singapore", "Asia/Shanghai", "Asia/Hong_Kong", "Asia/Tokyo", "Asia/Seoul",
    "Australia/Sydney", "Australia/Melbourne", "Australia/Perth", "Pacific/Auckland",
    "UTC"
]

async def async_setup_entry(hass, entry, async_add_entities):
    """Configura a seleção de Fuso Horário."""
    hub = hass.data[DOMAIN][entry.entry_id]
    
    if not hub.data:
        await hub.get_device_data()
        
    raw_tz = hub.data.get("timezone")
    if raw_tz is not None and raw_tz != -65535:
        async_add_entities([TholzTimezoneSelect(hub)], True)

class TholzTimezoneSelect(SelectEntity):
    """Seleção de Fuso Horário por Cidade."""

    def __init__(self, hub):
        self._hub = hub
        # MUDANÇA AQUI: Nome alterado para "Fuso Horário"
        self._attr_name = "Fuso Horário"
        self._attr_unique_id = f"tholz_{hub._host}_timezone_select"
        self._attr_icon = "mdi:map-clock"
        self._attr_options = TIMEZONES

    @property
    def device_info(self):
        return self._hub.device_info

    async def async_update(self):
        await self._hub.get_device_data()

    @property
    def current_option(self):
        current_offset_hours = self._hub.timezone 
        if current_offset_hours is None: return None
        now = dt_util.now()
        for tz_name in TIMEZONES:
            try:
                tz = zoneinfo.ZoneInfo(tz_name)
                offset_seconds = now.astimezone(tz).utcoffset().total_seconds()
                offset_hours = offset_seconds / 3600.0
                if abs(offset_hours - current_offset_hours) < 0.01:
                    return tz_name
            except Exception: continue
        return None

    async def async_select_option(self, option: str) -> None:
        try:
            tz = zoneinfo.ZoneInfo(option)
            now = dt_util.now()
            offset_seconds = now.astimezone(tz).utcoffset().total_seconds()
            offset_hours = offset_seconds / 3600.0
            await self._hub.set_timezone(offset_hours)
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"Erro ao definir fuso horário {option}: {e}")