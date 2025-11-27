import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from .const import DOMAIN

class TholzConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configura a integração Tholz via UI."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            # Validação simples (poderíamos testar conexão aqui)
            return self.async_create_entry(
                title=f"Tholz ({user_input[CONF_HOST]})", 
                data=user_input
            )

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)