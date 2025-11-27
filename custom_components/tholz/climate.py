import logging
import voluptuous as vol

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature, CONF_HOST
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Nomes
FAN_MODE_SILENT = "Silencioso"
FAN_MODE_SMART = "Inteligente"

async def async_setup_entry(hass, entry, async_add_entities):
    """Configuração via UI."""
    hub = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TholzClimate(hub)], True)

class TholzClimate(ClimateEntity):
    def __init__(self, hub):
        self._hub = hub
        # MUDANÇA AQUI: Nome alterado para "Aquecedor"
        self._attr_name = "Aquecedor"
        self._attr_unique_id = f"tholz_{hub._host}_climate"
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        
        self._attr_target_temperature_step = 1.0
        self._attr_min_temp = 18.0
        self._attr_max_temp = 40.0
        
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE | 
            ClimateEntityFeature.TURN_OFF | 
            ClimateEntityFeature.TURN_ON |
            ClimateEntityFeature.FAN_MODE
        )
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
        self._attr_fan_modes = [FAN_MODE_SILENT, FAN_MODE_SMART]

    @property
    def device_info(self):
        return self._hub.device_info

    async def async_update(self):
        await self._hub.get_device_data()

    @property
    def current_temperature(self):
        return self._hub.current_temperature

    @property
    def target_temperature(self):
        return self._hub.target_temperature

    @property
    def hvac_mode(self):
        op_mode = self._hub.heating_op_mode
        if op_mode == 4:
            return HVACMode.HEAT
        return HVACMode.OFF

    @property
    def fan_mode(self):
        mode = self._hub.heating_fan_mode
        if mode == 0:
            return FAN_MODE_SILENT
        return FAN_MODE_SMART

    async def async_set_fan_mode(self, fan_mode):
        if fan_mode == FAN_MODE_SILENT:
            await self._hub.set_heating_fan_mode(0)
        elif fan_mode == FAN_MODE_SMART:
            await self._hub.set_heating_fan_mode(1)
        await self.async_update()

    async def async_set_hvac_mode(self, hvac_mode):
        if hvac_mode == HVACMode.HEAT:
            await self._hub.set_heating_mode(4)
        elif hvac_mode == HVACMode.OFF:
            await self._hub.set_heating_mode(0)
        await self.async_update()

    async def async_set_temperature(self, **kwargs):
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        await self._hub.set_temperature(temp)
        await self.async_update()