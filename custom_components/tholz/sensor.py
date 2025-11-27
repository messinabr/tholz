import logging
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    hub = hass.data[DOMAIN][entry.entry_id]
    
    if not hub.data:
        await hub.get_device_data()

    sensors = [
        # Informações Gerais
        TholzSensor(hub, "Modelo", "device_model", "mdi:chip", None),
        TholzSensor(hub, "Status", "error_status", "mdi:alert-circle-outline", None),
        TholzSensor(hub, "Firmware", "firmware_version", "mdi:information-outline", None),
        
        # --- O SENSOR DE TEXTO "AQUECENDO" FOI REMOVIDO DAQUI ---
        # (Agora ele vive no binary_sensor.py)
        
        # Temperaturas
        TholzSensor(hub, "Temperatura Ambiente", "temp_t1", "mdi:earth", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
        TholzSensor(hub, "Temperatura Saída Trocador", "temp_t2", "mdi:heat-pump", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
        TholzSensor(hub, "Temperatura Piscina", "temp_t3", "mdi:pool", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    ]
    async_add_entities(sensors, True)

class TholzSensor(SensorEntity):
    def __init__(self, hub, name, attribute, icon, unit, device_class=None, state_class=None):
        self._hub = hub
        self._attr_name = name 
        self._attr_unique_id = f"tholz_{hub._host}_{attribute}"
        self._attribute = attribute
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def device_info(self):
        return self._hub.device_info

    async def async_update(self):
        await self._hub.get_device_data()

    @property
    def native_value(self):
        return getattr(self._hub, self._attribute)
