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
        # Cadeado para garantir que não haja duas conversas ao mesmo tempo
        self._lock = asyncio.Lock()

    async def get_device_data(self):
        """Conecta e atualiza os dados com sistema de tentativas (Retries)."""
        async with self._lock:
            # Tenta conectar até 3 vezes antes de desistir
            for attempt in range(1, 4):
                try:
                    reader, writer = await asyncio.wait_for(
                        asyncio.open_connection(self._host, self._port), timeout=5.0
                    )

                    payload = {"command": "getDevice"}
                    writer.write(json.dumps(payload).encode())
                    await writer.drain()

                    # Buffer de leitura
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
                    # Se for a última tentativa, grava o erro no log
                    if attempt == 3:
                        _LOGGER.warning(f"Tholz desconectado ou ocupado após 3 tentativas: {e}")
                    else:
                        # Se não for a última, apenas aguarda um pouco e tenta de novo (sem log de erro)
                        _LOGGER.debug(f"Tholz ocupado (Tentativa {attempt}/3). Retentando em 1s...")
                        await asyncio.sleep(1.0)
            
            return False

    async def send_command(self, argument):
        """Envia um comando de ESCRITA."""
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

        # Aguarda um pouco para o processador do Tholz respirar antes de ler novamente
        await asyncio.sleep(0.5)
        # Atualiza os dados para refletir a mudança no painel (usando a lógica de retry acima)
        # Nota: Chamamos self.get_device_data() fora do lock aqui, pois ele tem seu próprio lock,
        # mas como já estamos dentro do lock (async with self._lock), precisamos ter cuidado com deadlock.
        # CORREÇÃO: Vamos liberar o lock atual antes de chamar get_device_data novamente,
        # ou melhor, deixar o HA atualizar no próximo ciclo de polling.
        # Para simplificar e evitar deadlock, não forçamos atualização imediata aqui dentro do lock.
        
        # Apenas agenda uma atualização futura rápida se necessário, mas o polling normal cuidará disso.

    # --- Informações do Dispositivo ---
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": "Tholz Controlador",
            "manufacturer": "Tholz",
            "model": self.device_model,
            "sw_version": self.firmware_version,
        }

    # --- LEITURA DE DADOS ---
    def _get_temp_value(self, key):
        """Busca temperatura de forma inteligente."""
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

    @property
    def is_heating_active(self):
        try: return bool(self.data["heatings"]["heat0"]["on"])
        except (KeyError, TypeError): return False

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

    # --- Climate Props ---
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

    # --- Setters ---
    async def set_temperature(self, value):
        val_int = int(value * 10)
        argument = { "heatings": { "heat0": { "sp": val_int } } }
        await self.send_command(argument)
        # Força atualização logo após comando
        await asyncio.sleep(0.5)
        await self.get_device_data()

    async def set_heating_mode(self, mode):
        argument = { "heatings": { "heat0": { "opMode": int(mode) } } }
        await self.send_command(argument)
        await asyncio.sleep(0.5)
        await self.get_device_data()

    async def set_heating_fan_mode(self, mode):
        argument = { "heatings": { "heat0": { "fanMode": int(mode) } } }
        await self.send_command(argument)
        await asyncio.sleep(0.5)
        await self.get_device_data()

    async def set_output_state(self, output_key, state):
        argument = { "outputs": { output_key: { "on": state } } }
        await self.send_command(argument)
        await asyncio.sleep(0.5)
        await self.get_device_data()

    async def set_led_attributes(self, led_key, on=None, brightness=None, rgb_color=None, effect=None, speed=None):
        led_data = {}
        if on is not None: led_data["on"] = on
        if brightness is not None: led_data["brightness"] = int((brightness / 255) * 100)
        if rgb_color is not None:
            led_data["color"] = list(rgb_color)
            led_data["effect"] = 255
        if effect is not None: led_data["effect"] = effect
        if speed is not None: led_data["speed"] = int(speed)

        argument = { "leds": { led_key: led_data } }
        await self.send_command(argument)
    
    async def set_timezone(self, hours):
        seconds = int(hours * 3600)
        argument = { "timezone": seconds }
        await self.send_command(argument)
        await asyncio.sleep(0.5)
        await self.get_device_data()
