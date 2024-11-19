"""Roth Touchline SL sensors."""

from collections.abc import Callable
from dataclasses import dataclass

from pytouchlinesl import Zone

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import TouchlineSLConfigEntry
from .coordinator import TouchlineSLModuleCoordinator
from .entity import TouchlineSLZoneEntity


@dataclass(frozen=True, kw_only=True)
class TouchlineSLMeasurementSensorEntityDescription(SensorEntityDescription):
    """Describes Touchline measurement sensor entity."""

    value_fn: Callable[[Zone], StateType]


MEASUREMENT_SENSOR_TYPES: tuple[TouchlineSLMeasurementSensorEntityDescription, ...] = (
    TouchlineSLMeasurementSensorEntityDescription(
        key="battery_percent",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.BATTERY,
        translation_key="battery",
        value_fn=lambda status: status.battery_level,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TouchlineSLConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Touchline sensor entities."""

    coordinators = entry.runtime_data
    async_add_entities(
        TouchlineSLMeasurementSensor(
            coordinator=coordinator, zone_id=zone_id, description=description
        )
        for description in MEASUREMENT_SENSOR_TYPES
        for coordinator in coordinators
        for zone_id in coordinator.data.zones
    )


class TouchlineSLSensor(TouchlineSLZoneEntity, SensorEntity):
    """Defines a Touchline SL sensor."""

    def __init__(
        self,
        coordinator: TouchlineSLModuleCoordinator,
        zone_id: int,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize airgradient sensor."""
        super().__init__(coordinator, zone_id)
        self.entity_description = description
        self._attr_unique_id = f"module-{self.coordinator.data.module.id}-zone-{self.zone_id}-{description.key}"


class TouchlineSLMeasurementSensor(TouchlineSLSensor):
    """Defines a Touchling measurement sensor."""

    entity_description: TouchlineSLMeasurementSensorEntityDescription

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.zone)
