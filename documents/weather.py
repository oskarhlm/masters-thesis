from langchain_core.tools import tool
from enum import Enum
import os


class TempUnit(Enum):
    CELSIUS = 'Celsius'
    FAHRENHEIT = 'Fahrenheit'


class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.unit = TempUnit.CELSIUS  # Default unit

    def set_temperature_unit(self, temp_unit: TempUnit):
        self.unit = temp_unit

    def get_weather(self, location: str) -> str:
        # Example implementation with a placeholder return
        return f"Weather at {location} is 75° {self.unit.name}"


@tool
def get_current_weather(location: str, unit: TempUnit) -> str:
    weather_service = WeatherService(
        api_key=os.getenv('WEATHER_API_KEY'))
    weather_service.set_temperature_unit(unit)
    return weather_service.get_weather(location)
