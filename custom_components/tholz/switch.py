import logging
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN, get_output_info

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Configura as saídas via Config Flow."""
    # Pega o Hub compartilhado
    hub = hass.data[DOMAIN][entry.entry_id]
    
    # Garante que temos dados antes de criar as entidades
    if hub.data or await hub.get_device_data():
        switches = []
        outputs = hub.data.get("outputs", {})
        
        for key, value in outputs.items():
            # Se for nulo, ignora
            if value is None:
                continue
            
            # Cria a entidade
            switches.append(TholzSwitch(hub, key, value.get("id", 0)))
            
        async_add_entities(switches, True)

class TholzSwitch(SwitchEntity):
    def __init__(self, hub, output_key, output_id):
        self._hub = hub
        self._output_key = output_key
        self._output_id = output_id
        
        name_type, icon = get_output_info(output_id)
        
        self._attr_name = f"Tholz {name_type} ({output_key})"
        self._attr_unique_id = f"tholz_{hub._host}_{output_key}"
        self._attr_icon = icon

    @property
    def device_info(self):
        return self._hub.device_info

    async def async_update(self):
        await self._hub.get_device_data()

    @property
    def is_on(self):
        outputs = self._hub.data.get("outputs", {})
        output_data = outputs.get(self._output_key)
        if output_data:
            return output_data.get("on", False)
        return False

    async def async_turn_on(self, **kwargs):
        await self._hub.set_output_state(self._output_key, True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._hub.set_output_state(self._output_key, False)
        self.async_write_ha_state()