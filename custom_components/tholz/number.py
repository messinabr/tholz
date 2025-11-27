import logging
from homeassistant.components.number import NumberEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Configura apenas a velocidade dos LEDs (Number)."""
    hub = hass.data[DOMAIN][entry.entry_id]
    
    # Garante que temos dados
    if not hub.data:
        await hub.get_device_data()

    entities = []
    
    # Adiciona APENAS o controle de Velocidade dos LEDs
    leds = hub.data.get("leds", {})
    for key, value in leds.items():
        if value is not None:
            entities.append(TholzLedSpeed(hub, key))
            
    async_add_entities(entities, True)

class TholzLedSpeed(NumberEntity):
    """Controle de Velocidade do Efeito do LED."""

    def __init__(self, hub, led_key):
        self._hub = hub
        self._led_key = led_key
        self._attr_name = f"Tholz Velocidade LED ({led_key})"
        self._attr_unique_id = f"tholz_{hub._host}_{led_key}_speed"
        self._attr_icon = "mdi:speedometer"
        
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1

    @property
    def device_info(self):
        return self._hub.device_info

    async def async_update(self):
        await self._hub.get_device_data()

    @property
    def native_value(self):
        data = self._hub.data.get("leds", {}).get(self._led_key, {})
        return data.get("speed", 50)

    async def async_set_native_value(self, value: float) -> None:
        await self._hub.set_led_attributes(self._led_key, speed=value)
        self.async_write_ha_state()