import logging
from homeassistant.components.light import (
    LightEntity,
    ColorMode,
    LightEntityFeature,
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ATTR_EFFECT,
)
from .const import DOMAIN, THOLZ_EFFECTS, THOLZ_EFFECTS_NAMED

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Configura os LEDs via Config Flow."""
    hub = hass.data[DOMAIN][entry.entry_id]
    
    if hub.data or await hub.get_device_data():
        lights = []
        leds = hub.data.get("leds", {})
        
        for key, value in leds.items():
            if value is None:
                continue
            lights.append(TholzLight(hub, key))
            
        async_add_entities(lights, True)

class TholzLight(LightEntity):
    def __init__(self, hub, led_key):
        self._hub = hub
        self._led_key = led_key
        self._attr_name = f"Tholz LED ({led_key})"
        self._attr_unique_id = f"tholz_{hub._host}_{led_key}"
        self._attr_icon = "mdi:led-strip"
        
        self._attr_supported_color_modes = {ColorMode.RGB}
        self._attr_color_mode = ColorMode.RGB
        self._attr_supported_features = LightEntityFeature.EFFECT

    @property
    def device_info(self):
        return self._hub.device_info

    async def async_update(self):
        await self._hub.get_device_data()

    @property
    def is_on(self):
        data = self._hub.data.get("leds", {}).get(self._led_key, {})
        return data.get("on", False)

    @property
    def brightness(self):
        data = self._hub.data.get("leds", {}).get(self._led_key, {})
        val = data.get("brightness", 0)
        return int((val / 100) * 255)

    @property
    def rgb_color(self):
        data = self._hub.data.get("leds", {}).get(self._led_key, {})
        color = data.get("color", [255, 255, 255])
        return tuple(color)

    @property
    def effect_list(self):
        return list(THOLZ_EFFECTS.values())

    @property
    def effect(self):
        data = self._hub.data.get("leds", {}).get(self._led_key, {})
        effect_id = data.get("effect")
        return THOLZ_EFFECTS.get(effect_id, "Desconhecido")

    async def async_turn_on(self, **kwargs):
        on = True
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        rgb = kwargs.get(ATTR_RGB_COLOR)
        effect_name = kwargs.get(ATTR_EFFECT)
        
        effect_id = None
        if effect_name:
            effect_id = THOLZ_EFFECTS_NAMED.get(effect_name)

        await self._hub.set_led_attributes(
            self._led_key,
            on=on,
            brightness=brightness,
            rgb_color=rgb,
            effect=effect_id
        )
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._hub.set_led_attributes(self._led_key, on=False)
        self.async_write_ha_state()