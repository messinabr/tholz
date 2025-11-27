import asyncio
import json
import logging
import socket

from .const import PRODUCT_MODELS, ERROR_CODES, DOMAIN

_LOGGER = logging.getLogger(__name__)

class TholzHub:
    def __init__(self, host, port=4000):
        self._host = host
        self._port = port
        self.data = {}
        self._lock = asyncio.Lock()

    async def get_device_data(self):
        async with self._lock:
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(self._host, self._port), timeout=5.0
                )

                payload = {"command": "getDevice"}
                writer.write(json.dumps(payload).encode())
                await writer.drain()

                data = await asyncio.wait_for(reader.read(8192), timeout=5.0)
                response_text = data.decode()

                writer.close()
                await writer.wait_closed()

                if response_text:
                    json_data = json.loads(response_text)
                    if "response" in json_data:
                        self.data = json_data["response"]
                        return True
            except Exception as e:
                _LOGGER.warning(f"Tholz desconectado ou ocupado: {e}")
            
            return False

    async def send_command(self, argument):
        async with self._lock:
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(self._host, self._port), timeout=5.0
                )

                payload = {
                    "command": "setDevice",
                    "argument": argument
                }
                
                _LOGGER.debug(f"Enviando comando: {json.dumps(payload)}")
                
                writer.write(json.dumps(payload).encode())
                await writer.drain()

                try:
                    await asyncio.wait_for(reader.read(4096), timeout=3.0)
                except asyncio.TimeoutError:
                    pass

                writer.close()
                await writer.wait_closed()
                
            except Exception as e:
                _LOGGER.error(f"Erro ao enviar comando Tholz: {repr(e)}")
                return

        await asyncio.sleep(1.0)
        await self.get_device_data()

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": "Tholz Controlador",
            "manufacturer": "Tholz",
            "model": self.device_model,
            "sw_version": self.firmware_version,
        }

    # --- SENSORES DE TEMPERATURA ---
    def _get_temp_value(self, key):
        """Busca temperatura na raiz, em 'heatings/heat0' ou 'temperatures'."""
        val = self.data.get(key)
        if val is None:
            heat0 = self.data.get("heatings", {}).get("heat0", {})
            val = heat0.get(key)
        if val is None:
            temps = self.data.get("temperatures", {})
            val = temps.get(key)
        if val is not None:
            return val / 10.0
        return None

    @property
    def temp_t1(self): return self._get_temp_value("t1")
    @property
    def temp_t2(self): return self._get_temp_value("t2")
    @property
    def temp_t3(self): return self._get_temp_value("t3")

    # --- NOVO: Status do Aquecimento (Sim/Não) ---
    @property
    def heating_state_text(self):
        """Retorna Sim se a saída de aquecimento estiver ativa."""
        try:
            # Procura em heatings -> heat0 -> on
            is_on = self.data["heatings"]["heat0"]["on"]
            return "Sim" if is_on else "Não"
        except (KeyError, TypeError):
            return "Desconhecido"
    # ---------------------------------------------

    # --- Propriedades Gerais ---
    @property
    def device_model(self):
        model_id = self.data.get("id")
        return PRODUCT_MODELS.get(model_id, f"Desconhecido ({model_id})")

    @property
    def error_status(self):
        err_id = self.data.get("error", 0)
        return ERROR_CODES.get(err_id, f"Erro desconhecido ({err_id})")

    @property
    def firmware_version(self):
        return self.data.get("firmware", "N/A")

    @property
    def timezone(self):
        tz_seconds = self.data.get("timezone")
        if tz_seconds is not None and tz_seconds != -65535:
            return tz_seconds / 3600.0
        return None

    # --- Propriedades Climate ---
    @property
    def current_temperature(self): return self.temp_t3
    @property
    def target_temperature(self):
        try: return self.data["heatings"]["heat0"]["sp"] / 10.0
        except: return None
    @property
    def heating_op_mode(self):
        try: return self.data["heatings"]["heat0"]["opMode"]
        except: return 0
    @property
    def heating_fan_mode(self):
        try: return self.data["heatings"]["heat0"]["fanMode"]
        except:
            try: return self.data["heatings"]["heat0"]["fanmode"]
            except: return 1 

    # --- Métodos Setters ---
    async def set_temperature(self, value):
        val_int = int(value * 10)
        argument = { "heatings": { "heat0": { "sp": val_int } } }
        await self.send_command(argument)

    async def set_heating_mode(self, mode):
        argument = { "heatings": { "heat0": { "opMode": int(mode) } } }
        await self.send_command(argument)

    async def set_heating_fan_mode(self, mode):
        argument = { "heatings": { "heat0": { "fanMode": int(mode) } } }
        await self.send_command(argument)

    async def set_output_state(self, output_key, state):
        argument = { "outputs": { output_key: { "on": state } } }
        await self.send_command(argument)

    async def set_led_attributes(self, led_key, on=None, brightness=None, rgb_color=None, effect=None, speed=None):
        led_data = {}
        if on is not None: led_data["on"] = on
        if brightness is not None: led_data["brightness"] = int((brightness / 255) * 100)
        if rgb_color is not None: led_data["color"] = list(rgb_color)
        if effect is not None: led_data["effect"] = effect
        if speed is not None: led_data["speed"] = int(speed)

        argument = { "leds": { led_key: led_data } }
        await self.send_command(argument)

    async def set_timezone(self, hours):
        seconds = int(hours * 3600)
        argument = { "timezone": seconds }
        await self.send_command(argument)