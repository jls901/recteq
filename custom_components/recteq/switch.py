"""Recteq Switch Component."""
import logging

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.const import (
    CONF_NAME,
)

from homeassistant.core import callback


from .const import (
    CONF_LOCAL_KEY,
    DOMAIN,
    DPS_POWER,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config, add, discovery_info=None):
    entity = RecteqPowerSwitchEntity(
        hass.data[DOMAIN][config.entry_id],
        config.data.get(CONF_NAME, DOMAIN + "_" + config.data.get(CONF_LOCAL_KEY)),
    )
    add([entity])


class RecteqPowerSwitchEntity(CoordinatorEntity, SwitchEntity):
    """The Recteq switch to turn the unit on and off."""

    def __init__(self, coordinator, name):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._device = coordinator.grill_device
        self._name = f"{self._device.name} Power"
        self._is_on = (
            self._coordinator.data["dps"][DPS_POWER]
            if self._coordinator.data and "dps" in self._coordinator.data
            else False
        )
        self._device_class = SwitchDeviceClass.OUTLET

    @property
    def device_class(self):
        return self._device_class

    @property
    def unique_id(self):
        return f"{self._device.unique_id}.power"

    @property
    def device_info(self) -> {}:
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self._device.unique_id)},
            "name": self.name,
        }

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        _LOGGER.debug("Switching %s ON", self._name)
        self._device.set_status(DPS_POWER, True)
        await self._coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        _LOGGER.debug("Switching %s OFF", self._name)
        self._device.set_status(DPS_POWER, False)
        await self._coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self):
        if self._coordinator.data and "dps" in self._coordinator.data:
            self._is_on = self._coordinator.data["dps"][DPS_POWER]
            self.async_write_ha_state()
