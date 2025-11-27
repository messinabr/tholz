import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Configura o Sensor Binário (Aquecendo Agora)."""
    hub = hass.data[DOMAIN][entry.entry_id]
    
    if not hub.data:
        await hub.get_device_data()

    # Cria o sensor binário
    binary_sensors = [
        TholzBinarySensor(
            hub, 
            "Aquecendo Agora", 
            "mdi:fire"
        )
    ]
    async_add_entities(binary_sensors, True)

class TholzBinarySensor(BinarySensorEntity):
    """Sensor Binário que indica se está aquecendo."""

    def __init__(self, hub, name, icon):
        self._hub = hub
        self._attr_name = name
        self._attr_unique_id = f"tholz_{hub._host}_heating_active"
        self._attr_icon = icon
        # device_class=None mostra "Ligado/Desligado"
        # device_class="heat" mostraria "Quente/Normal"
        self._attr_device_class = None 

    @property
    def device_info(self):
        return self._hub.device_info

    async def async_update(self):
        await self._hub.get_device_data()

    @property
    def is_on(self):
        """Retorna True se estiver ligado, False caso contrário."""
        return self._hub.is_heating_active
