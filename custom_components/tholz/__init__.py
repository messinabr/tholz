import logging
from homeassistant.const import CONF_HOST, Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, DEFAULT_PORT
from .hub import TholzHub

_LOGGER = logging.getLogger(__name__)

# Lista de plataformas que vamos carregar
PLATFORMS = [Platform.CLIMATE, Platform.SENSOR, Platform.SWITCH, Platform.LIGHT, Platform.NUMBER, Platform.SELECT]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configura a integração a partir da UI."""
    host = entry.data[CONF_HOST]
    
    # Cria o Hub
    hub = TholzHub(host, DEFAULT_PORT)
    
    # Tenta primeira conexão
    await hub.get_device_data()
    
    # Salva o Hub na memória do HA para compartilhar entre as plataformas
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = hub
    
    # Carrega as plataformas (climate, sensor, etc)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Descarrega a integração."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
